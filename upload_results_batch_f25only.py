import db
from ll_entry_2022_6_28 import ll_entry
from mde_entry import read_mde,getGPS, read_pavtype
from calculate import calc
# from writefiles import writeELMOD_FWD, writeLCC, writeLCC0, writeLCC1
# from match_calc import match
import pickle as pkl
import report
import os, sys
from query_db import update_pavtype

import warnings
warnings.filterwarnings("ignore")

import tkinter as tk
from tkinter import *
from tkinter import filedialog

import traceback, re

import numpy as np



def delete_rows(con, tablename, id, verbose=1):
    # if(tablename != "stda_LONGLIST"):
    #     delstr = "DELETE FROM "+str(tablename)+" WHERE LONGLIST_ID = "+str(id)
    # else:
    #     delstr = "DELETE FROM "+str(tablename)+" WHERE ID = "+str(id)
    try:
        delstr = "DELETE FROM "+str(tablename)+" WHERE LONGLIST_ID = "+str(id)
        cursor = con.cursor()
        cursor.execute(delstr)
        con.commit()
    except:
        pass
    cursor.close()
    if verbose == 1:
        print("Removed illegal entries from ", tablename, "with id ", str(id))

def upload_single_result(args, f25_path,ll_no,year, con, warn_log_file_path, commit=0):

    # Specify default path to result folder here. 
    # result_folder = './Results/'
    # Specify default path to longlist excel here. #############

    # #### (Begin) Tkinter code to take user input
    # root = tk.Tk()
    # root.update_idletasks()
    # f25_path = filedialog.askopenfilename(initialdir='./',title='Select A F25 File', 
    #                                       filetypes=(("F25 files","*.F25"),("all files","*.*"))
    #                                      )

    # def get_inp_str(*kwargs):
    #     global inp_str,pavtype
    #     inp_str = myEntry.get()
    #     pavtype = str(clicked.get())
    #     root.quit()
    
    # Label(root, text="Enter the LL number and the year (separate by comma)", font=('Calibri 10')).pack()
    # myEntry = Entry(root)
    # myEntry.focus_force()
    # myEntry.pack()

    # ### Code for input pavement type (START)
    # tk.Label(root, text="Choose the pavement type.", font=('Calibri 10')).pack()
    # options = ["asphalt", "concrete", "composite"]
    # root.geometry("400x400")
    # clicked = tk.StringVar()
    # clicked.set('asphalt')
    # # tk.Label(root, text="Please choose pavement type: ")
    # drop = tk.OptionMenu(root, clicked, *options)
    # drop.pack()
    # # tk.Button(root, text='OK',command=_get).pack()
    # root.bind('<Return>', get_inp_str)
    # Button(root,text='OK',command=get_inp_str).pack(pady=10)
    # root.mainloop()
    # ### Code for input pavement type (END)
    # #### (End) Tkinter code to take user input

    # ll_no, year = inp_str.split(',')

    print('(Input) LL NO: {} , Year: {}'.format(ll_no,year))

    pkl_filename = os.path.join('./unused_var_dict/', 'LL-{}-{}.pkl'.format(ll_no,year))
    if not os.path.exists(pkl_filename):
        raise Exception('LL no and year combination is invalid. Can not find corresponding pickle file.')

    with open(pkl_filename, "rb") as f:
        unused_var_dict = pkl.load(f)

    mde_path = f25_path[:-3] + 'mde'

    assert mde_path != None, "Please give mde path"
    assert f25_path != None, "Please give f25 path"
    assert ll_no != None, "Please give long list number"
    # assert exl_path != None, "Please give excel sheet path"

    # Fix the f25 format issue, 3 spaces in front of 1,2,3
    

    # Extract Start and End GPS
    gpsx,gpsy = getGPS(f25_path)
    start_gps, end_gps = (gpsx[0], gpsy[0]), (gpsx[-1], gpsy[-1])

    ll_obj = unused_var_dict['ll_obj']

    # Decide Pavement type
    e1,e2= read_pavtype(mde_path, f25_path)
    
    # 2000 is the threshold for concrete
    if e1 >= 2000:
        pavtype = 'concrete'
    elif e2 >= 2000:
        pavtype = 'composite'
    else:
        pavtype = 'asphalt'

    print('e1={}, e2={}'.format(e1,e2))
    print('pavement type is: {}'.format(pavtype))
    assert (pavtype in ["asphalt", "concrete", "composite"]), print("Please input valid pavement type")

    # Assign the new pavement type
    ll_obj['pavtype'] = pavtype

    # Populate the LONGLIST table and get LONGLIST_ID (START)
    try:
        global id
        if args.debug:
            id,dir, lane_type = ll_entry(con, ll_no, f25_path, year, start_gps, end_gps, pavtype,commit=0)
        else:
            id,dir,lane_type = ll_entry(con, ll_no, f25_path, year, start_gps, end_gps, pavtype,commit=1) # change to commit=1 when in production
        ll_obj['dir'] = dir
    except:
        traceback_str = traceback.format_exc()
        if 'unique constraint' in traceback_str:
            print('Repeat entry of LL-{}-{}, this input is ignored...'.format(ll_no, year))
            # skip this entry and proceed with other entires
            return 
        else:
            print("LL-{}-{}: Error in performing calculations, please check".format(ll_no, year))
            print(traceback_str)
            delete_rows(con, "stda_LONGLIST", id)
            sys.exit(-1)
    # Populate the LONGLIST table and get LONGLIST_ID (END)

    # Read MDE (START)
    mde = None
    calc_data = None
    stats_data = None

    pcc_mod = None
    rxn_subg = None

    try:
        mde, roadtype, roadname, ll_obj = read_mde(con, mde_path, f25_path, id, ll_obj, args.server_root)
        ll_obj["roadname"] = roadname
    except:
        traceback_str = traceback.format_exc()
        print("LL-{}-{}: Error in reading mde, please check".format(ll_no, year))
        print(traceback_str)
        delete_rows(con, "stda_LONGLIST", id)
        sys.exit(-1)
    if 'mde_duplicate' in ll_obj:
        with open(warn_log_file_path, "a+") as f:
            print('Input F25 path: {}'.format(f25_path),file=f)
            print('Duplicate drop in MDE at {} \n'.format(ll_obj['duplicate_chainage']),file=f)
    if 'nomatch_msg' in ll_obj:
        with open(warn_log_file_path, "a+") as f:
            print('Input F25 path: {}'.format(f25_path),file=f)
            print(ll_obj['nomatch_msg']+'\n',file=f)


    row = unused_var_dict['row']
    
    # writeLCC(mde, pavtype)
    # Read MDE (END)

    try:
        calc_data, stats_data, mde, pcc_mod, rxn_subg = calc(con, id, pavtype, roadtype, row, mde)
    except:
        traceback_str = traceback.format_exc()
        print("LL-{}-{}: Error in performing calculations, please check".format(ll_no, year))
        print(traceback_str)
        delete_rows(con, "stda_LONGLIST", id)
        sys.exit(-1)

    try:
        if(commit):
            # print('[before put mde] mde deflections chainage: {}'.format(mde['deflections'][:,1]))
            db.putmde(con, mde, stats_data, id, commit=1)
            # print('[after put mde] mde deflections chainage: {}'.format(mde['deflections'][:,1]))
    except:
        traceback_str = traceback.format_exc()
        print("LL-{}-{}: Error in putting mde into DB, please check".format(ll_no, year))
        print(traceback_str)
        delete_rows(con, "stda_DEFLECTIONS", id)
        delete_rows(con, "stda_CALCULATED_DEFLECTIONS", id)
        delete_rows(con, "stda_MODULI_ESTIMATED", id)
        delete_rows(con, "stda_MISC", id)
        delete_rows(con, "stda_CALCULATIONS", id)
        delete_rows(con, "stda_STATS", id)
        delete_rows(con, "stda_LONGLIST", id)
        delete_rows(con, "stda_IMG", id)
        sys.exit(-1)

    # Image matching table
    try:
        if commit:
            # print('[before put img] mde deflections chainage: {}'.format(mde['deflections'][:,1]))
            db.putimg(con, ll_obj, id, year, lane_type, commit=1)
            # print('[after put img] mde deflections chainage: {}'.format(mde['deflections'][:,1]))
    except:
        traceback_str = traceback.format_exc()
        print("LL-{}-{}: Error in putting image matching into DB, please check".format(ll_no, year))
        print(traceback_str)
        delete_rows(con, "stda_DEFLECTIONS", id)
        delete_rows(con, "stda_CALCULATED_DEFLECTIONS", id)
        delete_rows(con, "stda_MODULI_ESTIMATED", id)
        delete_rows(con, "stda_MISC", id)
        delete_rows(con, "stda_CALCULATIONS", id)
        delete_rows(con, "stda_STATS", id)
        delete_rows(con, "stda_IMG", id)

        sys.exit(-1)


    try:
        if(commit):
            db.putcalc(con, calc_data, id, pcc_mod, rxn_subg)
            db.putstats(con, stats_data, id)
    except:
        traceback_str = traceback.format_exc()
        print("LL-{}-{}: Error in putting calculation and stats into DB, please check".format(ll_no, year))
        print(traceback_str)
        delete_rows(con, "stda._DEFLECTIONS", id)
        delete_rows(con, "stda_CALCULATED_DEFLECTIONS", id)
        delete_rows(con, "stda_MODULI_ESTIMATED", id)
        delete_rows(con, "stda_MISC", id)
        delete_rows(con, "stda_CALCULATIONS", id)
        delete_rows(con, "stda_STATS", id)
        delete_rows(con, "stda_LONGLIST", id)
        delete_rows(con, "stda_IMG", id)
        sys.exit(-1)

    # disable/enable report generation
    print('Report generation: ', args.gen_report)

    if args.gen_report:
        try:
            # print('[before gen_report] mde deflections chainage: {}'.format(mde['deflections'][:,1]))
            report.gen_report(ll_obj, mde, calc_data, stats_data, mde_path, f25_path, ll_no, year, con)
        except:
            traceback_str = traceback.format_exc()
            print("LL-{}-{}: Failed to generate report, please check flow".format(ll_no, year))
            print(traceback_str)
            delete_rows(con, "stda_DEFLECTIONS", id)
            delete_rows(con, "stda_CALCULATED_DEFLECTIONS", id)
            delete_rows(con, "stda_MODULI_ESTIMATED", id)
            delete_rows(con, "stda_MISC", id)
            delete_rows(con, "stda_CALCULATIONS", id)
            delete_rows(con, "stda_STATS", id)
            delete_rows(con, "stda_LONGLIST", id)
            delete_rows(con, "stda_IMG", id)
            sys.exit(-1)

if __name__ == "__main__":
    
    from pathlib import Path
    import argparse

    parser = argparse.ArgumentParser(description='Upload result in batch mode')
    parser.add_argument('--gen_report', action='store_true')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--server_root', type=str, default="\\\\dotwebp016vw/data/FWD/")
    parser.add_argument('--dev_env', action='store_true')
    args = parser.parse_args()

    # Read from external .txt where every line consists of the following:
    #   1. F25_path

    #### (Begin) Tkinter code to take user input
    txt_path = filedialog.askopenfilename(initialdir='./',title='Select An External .txt File', 
                                          filetypes=(("TXT files","*.txt"),("all files","*.*"))
                                         )
    print('txt path: ',txt_path)
    #### (End) Tkinter code to take user input

    #### Prepare the error log file
    err_log_dir = os.path.dirname(txt_path)
    input_txt_filename = os.path.basename(txt_path)[:-4]
    error_log_file = input_txt_filename +"_error_log.txt"
    warn_log_file = input_txt_filename +"_warn_log.txt"
    log_error_file_path = os.path.join(err_log_dir,error_log_file)
    warn_log_file_path = os.path.join(err_log_dir,warn_log_file)
    print('Error log is saved in: {}'.format(log_error_file_path))
    if os.path.exists(log_error_file_path):
        print('Overwrite previous error log!!!')
        os.remove(log_error_file_path)
    if os.path.exists(warn_log_file_path):
        os.remove(warn_log_file_path)

    con = db.connect(args.dev_env)

    with open(txt_path,'r') as file:
        Lines = file.readlines()
        
    # line_count = 0
    # Strips the newline character
    for line in Lines:
        # line_count += 1
        # print(line.strip())
        split_temp = line.strip().split('\\')
        # match 2 digits after "D" in request number to extract the year 
        year_temp = re.findall(r'D(\d{2})', split_temp[-3])
        assert len(year_temp)==1, print('Something went wrong when extracting the year number from request ID')
        year_2digits_str = year_temp[0]
        f25_path, year = line, int('20'+year_2digits_str)
        # Extract the ll_no using regex
        ll_no_temp = re.findall(r'LL\s?-?\s?(\d+)', split_temp[-2])
        # print('ll_no_temp: {}'.format(ll_no_temp))
        assert len(ll_no_temp) == 1, print('Something wrong when extracting the LL no from path...')
        ll_no =  ll_no_temp[0]
        # print('ll_no: {}'.format(ll_no))
        # Get rid of the double qoute when paste the path in Windows system
        f25_path = f25_path.replace('"', '').strip()
        # print(f25_path)
        # print('f25_path: {}'.format(f25_path))
        # print('ll_no: {}'.format(ll_no))
        # print('year: {}'.format(year))

        try:
            if args.debug:
                upload_single_result(args, f25_path, ll_no, year, con, warn_log_file_path, commit=0)
            else:
                upload_single_result(args, f25_path, ll_no, year, con, warn_log_file_path, commit=1) # change to commit=1 when in production
        except:
            traceback_str = traceback.format_exc()
            if 'unique constraint' in traceback_str:
                print('Repeat entry of {}-{}, this input is ignored...'.format(ll_no,year))
            else:
                with open(log_error_file_path, "a+") as f:
                    print('(Start of error log)#############LL-{} from year {}#######################'.format(ll_no,year),file=f)
                    print('Input F25 path: {}\n'.format(f25_path),file=f)
                    print(traceback_str,file=f)
                    delete_rows(con, "stda_DEFLECTIONS", id, verbose = 0)
                    delete_rows(con, "stda_CALCULATED_DEFLECTIONS", id, verbose=0)
                    delete_rows(con, "stda_MODULI_ESTIMATED", id, verbose = 0)
                    delete_rows(con, "stda_MISC", id, verbose = 0)
                    delete_rows(con, "stda_CALCULATIONS", id, verbose = 0)
                    delete_rows(con, "stda_STATS", id, verbose = 0)
                    delete_rows(con, "stda_LONGLIST", id, verbose = 0)
                    delete_rows(con, "stda_IMG", id)
                    print('Due to unexpected error, LL-{} from year {} is deleted...'.format(ll_no,year),file=f)
                    print('(End of error log)#############LL-{} from year {}#######################\n\n'.format(ll_no,year),file=f)

        # print("Line{}: {}".format(count, line.strip()))