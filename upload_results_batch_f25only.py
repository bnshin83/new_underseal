import db
from ll_query import ll_query
from mde_entry import read_mde,getGPS, read_pavtype
from calculate import calc
# from writefiles import writeELMOD_FWD, writeLCC, writeLCC0, writeLCC1
# from match_calc import match
import pickle as pkl
import report
import os, sys

import warnings
warnings.filterwarnings("ignore")

import tkinter as tk
from tkinter import *
from tkinter import filedialog

import traceback, re

import numpy as np

################################## Utils ##################################
def delete_rows(con, tablename, id, verbose=1):
    # if(tablename != "stda_LONGLIST"):
    #     delstr = "DELETE FROM "+str(tablename)+" WHERE LONGLIST_ID = "+str(id)
    # else:
    #     delstr = "DELETE FROM "+str(tablename)+" WHERE ID = "+str(id)
    delstr = "DELETE FROM "+str(tablename)+" WHERE LONGLIST_ID = "+str(id)
    cursor = con.cursor()
    cursor.execute(delstr)
    con.commit()
    cursor.close()
    if verbose == 1:
        print("Removed illegal entries from ", tablename, "with id ", str(id))

################################## Main ##################################
def upload_single_result(args, f25_path, req_no, ll_no, year, con, commit=0):

    # Preset id to none to prevent exit of batch uploading due to "id cannot find" error
    global id
    id = None

    print('(Input) Request NO. {}, LL NO: {} , Year: {}'.format(req_no, ll_no, year))

    pkl_filename = os.path.join('./unused_var_dict/', "LL-{}-{}".format(ll_no, year) + '.pkl')
    # if not os.path.exists(pkl_filename):
    #     raise Exception('LL no and year combination is invalid. Can not find corresponding pickle file.')

    with open(pkl_filename, "rb") as f:
        unused_var_dict = pkl.load(f)

    mde_path = f25_path[:-3] + 'mde'

    # Extract Start and End GPS
    gpsx, gpsy, gpsx_dict, gpsy_dict = getGPS(f25_path)
    if len(gpsx)>0 and len(gpsy)>0:
        start_gps, end_gps = (gpsx[0], gpsy[0]), (gpsx[-1], gpsy[-1])
    else:
        start_gps, end_gps = None, None

    ll_obj = unused_var_dict['ll_obj']

    # Decide Pavement type
    e1,e2= read_pavtype(mde_path, f25_path)
    
    if not args.special_case:
        # 2000 is the threshold for concrete
        if e1 >= 2000:
            pavtype = 'concrete'
        elif e2 >= 2000:
            pavtype = 'composite'
        else:
            pavtype = 'asphalt'
    else:
        # If it is the special case, manual enter the pavement type
        #### (Begin) Tkinter code to take user input
        root = tk.Tk()
        root.geometry("400x400")
        root.update_idletasks()

        def close_window():
            root.quit()

        tk.Label(root, text="Choose the pavement type.", font=('Calibri 10')).pack()
        options = ["asphalt", "concrete", "composite"]
        clicked = tk.StringVar(root)
        clicked.set('asphalt')
        drop = tk.OptionMenu(root, clicked, *options)
        drop.pack()
        Button(root,text='OK',command=close_window).pack(pady=10)
        root.bind("<Return>", lambda x: root.quit())
        root.mainloop()

        pavtype = str(clicked.get())
        ### Code for input pavement type (END)
        #### (End) Tkinter code to take user input

    print('e1={}, e2={}'.format(e1,e2))
    print('pavement type is: {}'.format(pavtype))
    if not (pavtype in ["asphalt", "concrete", "composite"]):
        raise Exception("Please input valid pavement type")

    # Assign the new pavement type
    ll_obj['pavtype'] = pavtype

    # Populate the LONGLIST table and get LONGLIST_ID (START)
    # try:

    if args.debug:
        id,dir, lane_type = ll_query(con, ll_no, f25_path, year, start_gps, end_gps, pavtype, args, commit=0)
    else:
        id,dir,lane_type = ll_query(con, ll_no, f25_path, year, start_gps, end_gps, pavtype, args, commit=1) # change to commit=1 when in production
    ll_obj['dir'] = dir
    # except:
    #     traceback_str = traceback.format_exc()
    #     if 'unique constraint' in traceback_str:
    #         print('Repeat entry of LL-{}-{} (Request NO. {}), this input is ignored...'.format(ll_no, year, req_no))
    #         # skip this entry and proceed with other entires
    #         return 
    #     else:
    #         # print(traceback_str)
    #         delete_rows(con, "stda_LONGLIST", id)
    #         raise Exception("LL-{}-{} (Request NO. {}): Error in performing calculations, please check. \n Trace Back: \n {}".format(ll_no, year, req_no,traceback_str))
        
    # Populate the LONGLIST table and get LONGLIST_ID (END)

    # Read MDE (START)
    mde = None
    calc_data = None
    stats_data = None

    pcc_mod = None
    rxn_subg = None

    # try:
    mde, roadtype, roadname, ll_obj = read_mde(con, mde_path, f25_path, id, ll_obj, gpsx, gpsy, gpsx_dict, gpsy_dict, args.server_root, args.skip_img_matching)
    ll_obj["roadname"] = roadname
    # except:
    #     traceback_str = traceback.format_exc()
    #     # print(traceback_str)
    #     delete_rows(con, "stda_LONGLIST", id)
    #     raise Exception("LL-{}-{} (Request NO. {}): Error in reading mde, please check. \n Trace Back: \n {}".format(ll_no, year, req_no, traceback_str))
    #     # sys.exit(-1)
    # if 'mde_duplicate' in ll_obj:
    #     with open(warn_log_file_path, "a+") as f:
    #         print('Input F25 path: {}'.format(f25_path),file=f)
    #         print('Duplicate drop in MDE at {} \n'.format(ll_obj['duplicate_chainage']),file=f)
    # if 'nomatch_msg' in ll_obj:
    #     with open(warn_log_file_path, "a+") as f:
    #         print('Input F25 path: {}'.format(f25_path),file=f)
    #         print(ll_obj['nomatch_msg']+'\n',file=f)


    # row = unused_var_dict['row']
    
    # writeLCC(mde, pavtype)
    # Read MDE (END)

    # try:
    calc_data, stats_data, mde, pcc_mod, rxn_subg = calc(con, id, pavtype, roadtype, ll_obj, mde, args.special_case)
    # except:
    #     traceback_str = traceback.format_exc()
    #     # print(traceback_str)
    #     delete_rows(con, "stda_LONGLIST", id)
    #     raise Exception("LL-{}-{} (Request NO. {}): Error in performing calculations, please check. \n Trace Back: \n {}".format(ll_no, year, req_no, traceback_str))
    #     # sys.exit(-1)

    # try:
    if(commit):
        # print('[before put mde] mde deflections chainage: {}'.format(mde['deflections'][:,1]))
        db.putmde(con, mde, stats_data, id, commit=1)
        # print('[after put mde] mde deflections chainage: {}'.format(mde['deflections'][:,1]))
    # except:
    #     traceback_str = traceback.format_exc()
    #     # print(traceback_str)
    #     delete_rows(con, "stda_DEFLECTIONS", id)
    #     delete_rows(con, "stda_CALCULATED_DEFLECTIONS", id)
    #     delete_rows(con, "stda_MODULI_ESTIMATED", id)
    #     delete_rows(con, "stda_MISC", id)
    #     delete_rows(con, "stda_CALCULATIONS", id)
    #     delete_rows(con, "stda_STATS", id)
    #     delete_rows(con, "stda_LONGLIST", id)
    #     delete_rows(con, "stda_IMG", id)
    #     raise Exception("LL-{}-{} (Request NO. {}): Error in putting mde into DB, please check\n Trace Back: \n {}".format(ll_no, year, req_no, traceback_str))
    #     # sys.exit(-1)

    # Image matching table
    # try:
    if commit:
        # print('[before put img] mde deflections chainage: {}'.format(mde['deflections'][:,1]))
        if not args.skip_img_matching:
            db.putimg(con, ll_obj, id, year, lane_type, commit=1)
        # print('[after put img] mde deflections chainage: {}'.format(mde['deflections'][:,1]))
    # except:
    #     traceback_str = traceback.format_exc()
        
    #     # print(traceback_str)
    #     delete_rows(con, "stda_DEFLECTIONS", id)
    #     delete_rows(con, "stda_CALCULATED_DEFLECTIONS", id)
    #     delete_rows(con, "stda_MODULI_ESTIMATED", id)
    #     delete_rows(con, "stda_MISC", id)
    #     delete_rows(con, "stda_CALCULATIONS", id)
    #     delete_rows(con, "stda_STATS", id)
    #     delete_rows(con, "stda_IMG", id)
    #     raise Exception("LL-{}-{} (Request NO. {}): Error in putting image matching into DB, please check. \n Trace Back: \n {}".format(ll_no, year, req_no, traceback_str))
    #     # sys.exit(-1)


    # try:
    if(commit):
        db.putcalc(con, calc_data, id, pcc_mod, rxn_subg)
        db.putstats(con, stats_data, id)
    # except:
    #     traceback_str = traceback.format_exc()
    #     # print(traceback_str)
    #     delete_rows(con, "stda_DEFLECTIONS", id)
    #     delete_rows(con, "stda_CALCULATED_DEFLECTIONS", id)
    #     delete_rows(con, "stda_MODULI_ESTIMATED", id)
    #     delete_rows(con, "stda_MISC", id)
    #     delete_rows(con, "stda_CALCULATIONS", id)
    #     delete_rows(con, "stda_STATS", id)
    #     delete_rows(con, "stda_LONGLIST", id)
    #     delete_rows(con, "stda_IMG", id)
    #     raise Exception("LL-{}-{} (Request NO. {}): Error in putting calculation and stats into DB, please check. \n Trace Back: \n {}".format(ll_no, year, req_no, traceback_str))
    #     # sys.exit(-1)

    # disable/enable report generation
    print('Report generation: ', args.gen_report)

    if args.gen_report:
        # try:
        # print('[before gen_report] mde deflections chainage: {}'.format(mde['deflections'][:,1]))
        report.gen_report(ll_obj, mde, calc_data, stats_data, mde_path, f25_path, ll_no, year, con, args.special_case)
        # except:
        #     traceback_str = traceback.format_exc()
        #     print(traceback_str)
        #     delete_rows(con, "stda_DEFLECTIONS", id)
        #     delete_rows(con, "stda_CALCULATED_DEFLECTIONS", id)
        #     delete_rows(con, "stda_MODULI_ESTIMATED", id)
        #     delete_rows(con, "stda_MISC", id)
        #     delete_rows(con, "stda_CALCULATIONS", id)
        #     delete_rows(con, "stda_STATS", id)
        #     delete_rows(con, "stda_LONGLIST", id)
        #     delete_rows(con, "stda_IMG", id)
        #     raise Exception("LL-{}-{} (Request NO. {}): Failed to generate report, please check flow. \n Trace Back: \n{}".format(ll_no, year, req_no,traceback_str))
        #     # sys.exit(-1)

if __name__ == "__main__":
    
    from pathlib import Path
    import argparse

    parser = argparse.ArgumentParser(description='Upload result in batch mode')
    parser.add_argument('--gen_report', action='store_true')
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--special_case', action='store_true')
    parser.add_argument('--server_root', type=str, default="\\\\dotwebp016vw/data/FWD/")
    parser.add_argument('--dev_env', type=str, default="shin",choices=['dev_wen', 'shin', 'ecn_wen','ecn_shin'])
    parser.add_argument('--skip_img_matching', action='store_true')
    args = parser.parse_args()

    # Read from external .txt where every line consists of the following:
    #   1. F25_path

    #### (Begin) Tkinter code to take user input
    if args.dev_env != 'dev_wen':
        txt_path = filedialog.askopenfilename(initialdir='./',title='Select An External .txt File', 
                                            filetypes=(("TXT files","*.txt"),("all files","*.*"))
                                            )
    else:
        txt_path = filedialog.askopenfilename(initialdir='D:/indot_proj/Underseal/result_folder/', title='Select An External .txt File', 
                                            filetypes=(("TXT files","*.txt"),("all files","*.*"))
                                            )
    print('txt path: ',txt_path)
    #### (End) Tkinter code to take user input

    #### Prepare the error log file
    err_log_dir = os.path.dirname(txt_path)
    input_txt_filename = os.path.basename(txt_path)[:-4]
    error_log_file = input_txt_filename +"_error_log.txt"
    warn_log_file = input_txt_filename +"_warn_log.txt"
    filename_error_log_file = input_txt_filename +"_filename_error_log.txt"
    log_error_file_path = os.path.join(err_log_dir,error_log_file)
    warn_log_file_path = os.path.join(err_log_dir,warn_log_file)
    filename_error_log_path = os.path.join(err_log_dir,filename_error_log_file)
    print('Error log is saved in: {}'.format(log_error_file_path))
    if os.path.exists(log_error_file_path):
        print('Overwrite previous error log!!!')
        os.remove(log_error_file_path)
    if os.path.exists(warn_log_file_path):
        os.remove(warn_log_file_path)
    if os.path.exists(filename_error_log_path):
        os.remove(filename_error_log_path)

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
        if not len(year_temp)==1:
            raise Exception('Something went wrong when extracting the year number from request ID')
        year_2digits_str = year_temp[0]
        f25_path, year = line, int('20'+year_2digits_str)
        # Extract the ll_no using regex
        ll_no_temp = re.findall(r'LL\s?-?\s?(\d+)', split_temp[-2])
        # extract Request NO., and remove the white space
        req_no = split_temp[-3].replace(" ", "")
        # print('ll_no_temp: {}'.format(ll_no_temp))
                # Find LL NO in DB
        sqlstr = """
                 SELECT longlist_no FROM stda_longlist_info
                 WHERE request_no='""" + str(req_no) + """'
                 """
        cursor = con.cursor()
        cursor.execute(sqlstr)
        for result in cursor:
            ll_no = str(result[0])
        cursor.close()
        # print('ll_no: {}'.format(ll_no))
        # Get rid of the double qoute when paste the path in Windows system
        f25_path = f25_path.replace('"', '').strip()
        # print(f25_path)
        # print('f25_path: {}'.format(f25_path))
        # print('ll_no: {}'.format(ll_no))
        # print('year: {}'.format(year))

        try:
            if args.debug:
                upload_single_result(args, f25_path, req_no, ll_no, year, con, commit=0)
            else:
                upload_single_result(args, f25_path, req_no, ll_no, year, con, commit=1) # change to commit=1 when in production
        except:
            traceback_str = traceback.format_exc()
            if 'unique constraint' in traceback_str:
                print('Repeat entry of {}-{}, this input is ignored...'.format(ll_no,year))
            elif "F25 filename does not meet requirement" in traceback_str:
                with open(filename_error_log_path, "a+") as filename_log_f:
                    print("{}\n".format(f25_path),file=filename_log_f)
            else:
                with open(log_error_file_path, "a+") as f:
                    print('(Start of error log)#############LL-{} from year {} (Request NO. {})#######################'.format(ll_no,year,req_no),file=f)
                    print('Input F25 path: {}\n'.format(f25_path),file=f)
                    print(traceback_str,file=f)
                    # If there is error happen before uploading anything, there is nothing to delete.
                    # It would cause error and exit the batch uploading if we try to delete something that does not exist
                    if id:
                        delete_rows(con, "stda_DEFLECTIONS", id, verbose = 0)
                        delete_rows(con, "stda_CALCULATED_DEFLECTIONS", id, verbose=0)
                        delete_rows(con, "stda_MODULI_ESTIMATED", id, verbose = 0)
                        delete_rows(con, "stda_MISC", id, verbose = 0)
                        delete_rows(con, "stda_CALCULATIONS", id, verbose = 0)
                        delete_rows(con, "stda_STATS", id, verbose = 0)
                        delete_rows(con, "stda_LONGLIST", id, verbose = 0)
                        delete_rows(con, "stda_IMG", id, verbose = 0)
                    print('Due to unexpected error, LL-{} from year {} is deleted...'.format(ll_no,year),file=f)
                    print('(End of error log)#############LL-{} from year {} (Request NO. {})#######################\n\n'.format(ll_no,year,req_no),file=f)
                

        # print("Line{}: {}".format(count, line.strip()))

    print("\n Uploading finished!!!")