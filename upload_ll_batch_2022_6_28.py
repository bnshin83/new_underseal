import os, warnings, sys
import string
warnings.filterwarnings("ignore")

import db
from ll_info_entry_2022 import ll_info_entry
import pickle as pkl

from tkinter import *
from tkinter import filedialog

import numpy as np

import traceback



COMMIT = 1
CON = db.connect()

def delete_rows(con, tablename, id):
    delstr = "DELETE FROM "+str(tablename)+" WHERE LONGLIST_INFO_ID = "+str(id)
    cursor = con.cursor()
    cursor.execute(delstr)
    con.commit()
    cursor.close()
    print("Removed illegal entries from ", tablename, "with id ", str(id))

def upload_single_ll(con, exl_path=None, ll_no=None, year=None):

    assert isinstance(ll_no, int), "Please enter valid LL number"

    assert ll_no != None, "Please give long list number"
    assert exl_path != None, "Please give excel sheet path"
    
    id = None
    row = None # will be used in "calc"
    roadtype = None # will be used in "calc" as argument
    ll_obj = None # will be used in "report"

    pavtype='TBD'
    # pavtype = excel.return_value(read_row, 'Pavement Type')
    # assert pavtype in ['asphalt','concrete','composite']

    # try:
    ll_info_id,row, ll_obj = ll_info_entry(con, exl_path, year, ll_no)
    if(COMMIT == 0):
        delete_rows(con, "STDA.STDA_LONGLIST_INFO", ll_info_id)
    # except Exception as e:
    #     print("Couldn't read Longlist and put it back into DB. Please check")
    #     print(e)
    #     if(id != None):
    #         delete_rows(con, "STDA.STDA_LONGLIST_INFO", id)    
    #     sys.exit(-1)

    # store variable in dict for future use
    # id is the unique ll_id
    # this id will keep increasing even if we deleted the row??
    unused_var_dict = {}
    unused_var_dict['row'] = row
    unused_var_dict['roadtype'] = roadtype
    unused_var_dict['ll_obj'] = ll_obj
    unused_var_dict['exl_path'] = exl_path

    pkl_filename = 'LL-{}-{}'.format(ll_no,year)

    # check for "unused_var_dict" folder existence
    unused_var_dict_folder = './unused_var_dict'
    if not os.path.exists(unused_var_dict_folder):
        os.makedirs(unused_var_dict_folder)

    filename = '{}/{}.pkl'.format(unused_var_dict_folder, pkl_filename)
    # print(filename)
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, "wb") as f:
        pkl.dump(unused_var_dict, f)


def upload_ll_batch(con):

    exl_path = filedialog.askopenfilename(initialdir='./',title='Select A Long List File', 
                                          filetypes=(("xlsx files","*.xlsx"),("all files","*.*"))
                                         )
    
    # Will support year longlist excel sheet up to year of 2999
    # Probably we can have a more efiicient way to find the year 
    # if the LL file naming convention is known
    for year_tryout in range(2010,2999):
        if str(year_tryout) in exl_path:
            print('Year {} long list is used...'.format(year_tryout))
            year = str(year_tryout)
            break
    
    #### (Begin) Tkinter code to take user input
    def get_inp_str(event):
        global inp_str
        inp_str = myEntry.get()
        root.quit()
    
    root= Tk()
    Label(root, text="Enter the LL numbers (separate by comma)", font=('Calibri 10')).pack()
    myEntry = Entry(root)
    myEntry.focus_force()
    myEntry.pack()
    Button(root,text='OK',command=get_inp_str).pack(pady=10)
    root.bind('<Return>', get_inp_str)
    root.mainloop()
    #### (End) Tkinter code to take user input

    # extract user input
    input_list = [elem for elem in inp_str.split(',')]

    ll_no_list = []
    for single_elem in input_list:
        if '-' in single_elem:
            start_ll = int(single_elem.split('-')[0])
            end_ll = int(single_elem.split('-')[1])
            ll_no_list.extend(list(range(start_ll,end_ll+1)))
        else:
            ll_no_list.append(int(single_elem))
        
    ll_no_set = set(ll_no_list)
    for single_ll in ll_no_set:
        try:
            upload_single_ll(con, exl_path=exl_path, ll_no=single_ll, year=year)
        except:
            traceback_str = traceback.format_exc()
            if 'unique constraint' in traceback_str:
                print('Repeat entry of {}, this input is ignored...'.format(single_ll))
            else:
                print('Unexpected error when uploading {}...'.format(single_ll))
                print(traceback_str)

upload_ll_batch(con=CON)