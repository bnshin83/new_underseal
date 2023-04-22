import db
from ll_entry_2022_6_28 import ll_entry
from mde_entry import read_mde,getGPS
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

import traceback

COMMIT = 1

def delete_rows(con, tablename, id):
    # if(tablename != "STDA.STDA_LONGLIST"):
    #     delstr = "DELETE FROM "+str(tablename)+" WHERE LONGLIST_ID = "+str(id)
    # else:
    #     delstr = "DELETE FROM "+str(tablename)+" WHERE ID = "+str(id)
    delstr = "DELETE FROM "+str(tablename)+" WHERE LONGLIST_ID = "+str(id)
    cursor = con.cursor()
    cursor.execute(delstr)
    con.commit()
    cursor.close()
    print("Removed illegal entries from ", tablename, "with id ", str(id))

def main():

    # Specify default path to result folder here. 
    # result_folder = './Results/'
    # Specify default path to longlist excel here. #############

    con = db.connect()
    mde_path = None
    f25_path = None
    ll_no = None # going to get it from DB..

    #### (Begin) Tkinter code to take user input
    root = tk.Tk()
    root.update_idletasks()
    f25_path = filedialog.askopenfilename(initialdir='./',title='Select A F25 File', 
                                          filetypes=(("F25 files","*.F25"),("all files","*.*"))
                                         )

    def get_inp_str(*kwargs):
        global inp_str,pavtype
        inp_str = myEntry.get()
        pavtype = str(clicked.get())
        root.quit()
    
    Label(root, text="Enter the LL number and the year (separate by comma)", font=('Calibri 10')).pack()
    myEntry = Entry(root)
    myEntry.focus_force()
    myEntry.pack()

    ### Code for input pavement type (START)
    tk.Label(root, text="Choose the pavement type.", font=('Calibri 10')).pack()
    options = ["asphalt", "concrete", "composite"]
    root.geometry("400x400")
    clicked = tk.StringVar()
    clicked.set('asphalt')
    # tk.Label(root, text="Please choose pavement type: ")
    drop = tk.OptionMenu(root, clicked, *options)
    drop.pack()
    # tk.Button(root, text='OK',command=_get).pack()
    root.bind('<Return>', get_inp_str)
    Button(root,text='OK',command=get_inp_str).pack(pady=10)
    root.mainloop()
    ### Code for input pavement type (END)
    #### (End) Tkinter code to take user input

    ll_no, year = inp_str.split(',')
    print('(Input) LL NO: {} , Year: {}'.format(ll_no,year))
    print('pavemnt type is: {}'.format(pavtype))

    assert (pavtype in ["asphalt", "concrete", "composite"]), print("Please input valid pavement type")

    pkl_filename = os.path.join('./unused_var_dict/', 'LL-{}-{}.pkl'.format(ll_no,year))
    if not os.path.exists(pkl_filename):
        raise Exception('LL no and year combination is invalid. Can not find corresponding pickle file.')

    with open(pkl_filename, "rb") as f:
        unused_var_dict = pkl.load(f)

    mde_path = f25_path[:-3] + 'mde'

    ll_obj = unused_var_dict['ll_obj']
    # Assign the new pavement type becuase default pavtype is 'TBD'
    ll_obj['pavtype'] = pavtype
    row = unused_var_dict['row']
    # exl_path = unused_var_dict['exl_path']

    assert mde_path != None, "Please give mde path"
    assert f25_path != None, "Please give f25 path"
    assert ll_no != None, "Please give long list number"
    # assert exl_path != None, "Please give excel sheet path"
    assert pavtype != None, "Please give pavement type"

    # Extract Start and End GPS
    gpsx,gpsy = getGPS(f25_path)
    start_gps, end_gps = (gpsx[0], gpsy[0]), (gpsx[-1], gpsy[-1])

    # Populate the LONGLIST table and get LONGLIST_ID (START)
    try:
        id,dir = ll_entry(con, ll_no, f25_path, year, start_gps, end_gps)
        ll_obj['dir'] = dir
    except Exception as e:
        print("Error in uploading to STDA.STDA._LONGLIST table, please check")
        print(e)
        delete_rows(con, "STDA.STDA_LONGLIST", id)
        sys.exit(-1)
    # Populate the LONGLIST table and get LONGLIST_ID (END)

    mde = None
    calc_data = None
    stats_data = None

    pcc_mod = None
    rxn_subg = None

    try:
        mde, roadtype, roadname = read_mde(con, mde_path, f25_path, id)
        ll_obj["roadname"] = roadname
    except Exception as e:
        print("Error in reading mde, please check")
        print(e)
        delete_rows(con, "STDA.STDA_LONGLIST", id)
        sys.exit(-1)
    

    # writeLCC(mde, pavtype)

    try:
        calc_data, stats_data, mde, pcc_mod, rxn_subg = calc(con, id, pavtype, roadtype, row, mde)
    except Exception as e:
        print("Error in performing calculations, please check")
        print(e)
        delete_rows(con, "STDA.STDA_LONGLIST", id)
        sys.exit(-1)

    try:
        if(COMMIT):
            # print("Commiting to mde?")
            db.putmde(con, mde, id)
            # print("Committed to MDE!")
    except Exception as e:
        print("Error in putting mde into DB, please check")
        print(e)
        delete_rows(con, "STDA.STDA_DEFLECTIONS", id)
        delete_rows(con, "STDA.STDA_CALCULATED_DEFLECTIONS", id)
        delete_rows(con, "STDA.STDA_MODULI_ESTIMATED", id)
        delete_rows(con, "STDA.STDA_MISC", id)
        delete_rows(con, "STDA.STDA_CALCULATIONS", id)
        delete_rows(con, "STDA.STDA_STATS", id)
        delete_rows(con, "STDA.STDA_LONGLIST", id)
        sys.exit(-1)

    try:
        if(COMMIT):
            db.putcalc(con, calc_data, id, pcc_mod, rxn_subg)
            db.putstats(con, stats_data, id)
    except Exception as e:
        print("Error in putting calculation and stats into DB, please check")
        print(e)
        delete_rows(con, "STDA.STDA_DEFLECTIONS", id)
        delete_rows(con, "STDA.STDA_CALCULATED_DEFLECTIONS", id)
        delete_rows(con, "STDA.STDA_MODULI_ESTIMATED", id)
        delete_rows(con, "STDA.STDA_MISC", id)
        delete_rows(con, "STDA.STDA_CALCULATIONS", id)
        delete_rows(con, "STDA.STDA_STATS", id)
        delete_rows(con, "STDA.STDA_LONGLIST", id)
        sys.exit(-1)

    try:
        report.gen_report(ll_obj, mde, calc_data, stats_data, mde_path, f25_path, ll_no, year, con)
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("Failed to generate report, please check flow")
        print(traceback_str)
        delete_rows(con, "STDA.STDA_DEFLECTIONS", id)
        delete_rows(con, "STDA.STDA_CALCULATED_DEFLECTIONS", id)
        delete_rows(con, "STDA.STDA_MODULI_ESTIMATED", id)
        delete_rows(con, "STDA.STDA_MISC", id)
        delete_rows(con, "STDA.STDA_CALCULATIONS", id)
        delete_rows(con, "STDA.STDA_STATS", id)
        delete_rows(con, "STDA.STDA_LONGLIST", id)
        sys.exit(-1)

    # Modify the long list and put in the pavement type   
    update_pavtype(con,
                   table_name="STDA.STDA_longlist_info",
                   update_col='pavtype',
                   new_value=pavtype,
                   ll_no=ll_no,
                   year=year)

main()