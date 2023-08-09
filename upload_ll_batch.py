import os, warnings, sys
import string
warnings.filterwarnings("ignore")

import db
from ll_info_entry import ll_info_entry
import pickle as pkl

from tkinter import *
from tkinter import filedialog

import numpy as np
import traceback
import argparse
import pandas as pd
import re

parser = argparse.ArgumentParser(description='Upload LL entires batch mode')
parser.add_argument('--dev_env', action='store_true')
args = parser.parse_args()

COMMIT = 1
CON = db.connect(args.dev_env)

def delete_rows(con, tablename, id):
    delstr = "DELETE FROM "+str(tablename)+" WHERE LONGLIST_INFO_ID = "+str(id)
    cursor = con.cursor()
    cursor.execute(delstr)
    con.commit()
    cursor.close()
    print("Removed illegal entries from ", tablename, "with longlist_info id:", str(id))

def upload_single_ll(con, ll_info_df, ll_no_colname, ll_no, combine_flag, xls_filename_year, duplicate_check_set):

    assert isinstance(ll_no, int), "Please enter valid LL number"
    
    # row = None # will be used in "calc"
    roadtype = None # will be used in "calc" as argument
    ll_obj = None # will be used in "report"

    # pavtype='TBD'
    # assert pavtype in ['asphalt','concrete','composite']

    try:
        ll_info_id, ll_obj = ll_info_entry(con, ll_info_df, ll_no_colname, ll_no, xls_filename_year, combine_flag)
        if(COMMIT == 0):
            delete_rows(con, "STDA.STDA_LONGLIST_INFO", ll_info_id)
    except Exception as e:
        print("Couldn't read Longlist and put it back into DB. Please check")
        print(e)
        delete_rows(con, "STDA.STDA_LONGLIST_INFO", ll_info_id)    
        sys.exit(-1)

    # store variable in dict for future use
    # id is the unique ll_id
    # this id will keep increasing even if we deleted the row??
    unused_var_dict = {}
    # unused_var_dict['row'] = row
    unused_var_dict['roadtype'] = roadtype
    unused_var_dict['ll_obj'] = ll_obj

    pkl_filename = "LL-{}-{}".format(ll_no, xls_filename_year) + '.pkl'

    # check for "unused_var_dict" folder existence
    unused_var_dict_folder = './unused_var_dict'
    if not os.path.exists(unused_var_dict_folder):
        os.makedirs(unused_var_dict_folder)

    filename = '{}/{}'.format(unused_var_dict_folder, pkl_filename)
    # print(filename)
    if filename not in duplicate_check_set:
        duplicate_check_set.add(filename)
    else:
        raise Exception('Duplicate Request NO.: {} in {} LL sheet'.format(ll_obj['req no'], xls_filename_year))
    
    # Overwrite previous uploaded LL entires
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, "wb") as f:
        pkl.dump(unused_var_dict, f)


def upload_ll_batch(con):
    
    if not args.dev_env:
        exl_path = filedialog.askopenfilename(initialdir='./',title='Select A Long List File', 
                                          filetypes=(("xlsx files","*.xlsx"),("all files","*.*"))
                                         )
    else:
        exl_path = filedialog.askopenfilename(initialdir='D:/indot_proj/Underseal/result_folder/',title='Select A Long List File', 
                                          filetypes=(("xlsx files","*.xlsx"),("all files","*.*"))
                                         )
    
    # find the year digits in the excel filename
    xls_filename = os.path.basename(exl_path)
    pattern = r'(?<!\d)\d{4}(?!\d)'
    xls_filename_year_list = re.findall(pattern, xls_filename)
    assert len(xls_filename_year_list) == 1
    xls_filename_year = xls_filename_year_list[0]
    # Find if the excel if combined sheet
    combine_flag = 'combine' in os.path.basename(exl_path)
    # find the sheetname for ll info
    if not combine_flag and int(xls_filename_year)>2022:
        sheet_name = "Test Request Overview"
        ll_no_colname = "LL"
    else:
        sheet_name = "Test Request Overview"
        ll_no_colname = "Long List Number"
    ll_info_df = pd.read_excel(exl_path, sheet_name=sheet_name)
    #### (Begin) Tkinter code to take user input
    def close_window():
        root.quit()
    
    root= Tk()
    Label(root, text="Enter the LL numbers (separate by comma). You can use 'end' to indicate the last LL NO.", font=('Calibri 10')).pack()
    myEntry = Entry(root)
    myEntry.focus_force()
    myEntry.pack()
    Button(root,text='OK',command=close_window).pack(pady=10)
    root.bind('<Return>', lambda x: root.quit())
    root.mainloop()
    #### (End) Tkinter code to take user input

    # extract user input
    inp_str = myEntry.get()
    input_list = [elem for elem in inp_str.split(',')]

    ll_no_list = []
    for single_elem in input_list:
        if '-' in single_elem:
            start_ll = int(single_elem.split('-')[0])
            end_str = single_elem.split('-')[1]
            if end_str.isnumeric():
                end_ll = int(end_str)
            # if the "end" is used in the user input
            elif "end" in end_str:
                largest_ll = ll_info_df[ll_no_colname].max()
                end_ll = int(largest_ll)
            else:
                raise Exception('End index is not valid')
            ll_no_list.extend(list(range(start_ll,end_ll+1)))
        else:
            ll_no_list.append(int(single_elem))
        
    # Check if there are duplicate LL No.
    ll_no_set = set(ll_no_list)
    assert len(ll_no_set) == len(ll_no_list)

    # Check for duplicate Request No.
    duplicate_check_set = set()

    # log the error
    error_log_dir = os.path.dirname(exl_path)
    # extension name is ".xlsx", so [:-5]
    error_log_filanme = os.path.basename(exl_path)[:-5] + "_error_log.txt"
    log_error_file_path = os.path.join(error_log_dir,error_log_filanme)
    if os.path.exists(log_error_file_path):
        print('Overwrite previous LL upload error log!!!')
        os.remove(log_error_file_path)

    for single_ll_no in ll_no_list:
        try:
            upload_single_ll(con, ll_info_df, ll_no_colname, single_ll_no, combine_flag, xls_filename_year, duplicate_check_set)
        except:
            traceback_str = traceback.format_exc()
            if 'unique constraint' in traceback_str:
                print('Repeat entry of {}, this input is ignored...'.format(single_ll_no))
            else:
                with open(log_error_file_path, "a+") as f:
                    print('Unexpected error when uploading LL NO. {}...'.format(single_ll_no),file=f)
                    print(traceback_str,file=f)
                    print("########################################################################\n",file=f)

upload_ll_batch(con=CON)