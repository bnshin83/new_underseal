import os
import sys
import string
import warnings
import pickle as pkl
import argparse
import traceback

import numpy as np
from tkinter import Tk, Label, Entry, Button, filedialog

import db
from ll_info_entry import ll_info_entry

warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(description='Upload LL entries in batch mode')
parser.add_argument('--dev_env', action='store_true')
args = parser.parse_args()

COMMIT = 1
CON = db.connect(args.dev_env)


def delete_rows(con, tablename, id):
    delstr = f"DELETE FROM {tablename} WHERE LONGLIST_INFO_ID = {id}"
    cursor = con.cursor()
    cursor.execute(delstr)
    con.commit()
    cursor.close()
    print(f"Removed illegal entries from {tablename} with longlist_info id: {id}")


def upload_single_ll(con, exl_path=None, ll_no=None, year=None):
    if ll_no is None or exl_path is None:
        raise ValueError("Please provide a valid LL number and Excel sheet path")

    unused_var_dict = {'roadtype': None, 'll_obj': None, 'exl_path': exl_path}
    ll_info_id, ll_obj = None, None

    try:
        ll_info_id, ll_obj = ll_info_entry(con, exl_path, year, ll_no)
        if COMMIT == 0:
            delete_rows(con, "STDA.STDA_LONGLIST_INFO", ll_info_id)
    except Exception as e:
        print("Couldn't read Longlist and put it back into DB. Please check")
        print(e)
        if ll_info_id is not None:
            delete_rows(con, "STDA.STDA_LONGLIST_INFO", ll_info_id)
        sys.exit(-1)

    unused_var_dict['ll_obj'] = ll_obj
    pkl_filename = f'LL-{ll_no}-{year}'
    unused_var_dict_folder = './unused_var_dict'

    if not os.path.exists(unused_var_dict_folder):
        os.makedirs(unused_var_dict_folder)

    filename = f'{unused_var_dict_folder}/{pkl_filename}.pkl'
    if os.path.exists(filename):
        os.remove(filename)

    with open(filename, "wb") as f:
        pkl.dump(unused_var_dict, f)


def get_input_list():
    def close_window():
        root.quit()

    root = Tk()
    Label(root, text="Enter the LL numbers (separate by comma)", font=('Calibri 10')).pack()
    myEntry = Entry(root)
    myEntry.focus_force()
    myEntry.pack()
    Button(root, text='OK', command=close_window).pack(pady=10)
    root.bind('<Return>', lambda x: root.quit())
    root.mainloop()

    return myEntry.get()


def parse_input_list(input_str):
    input_list = [elem for elem in input_str.split(',')]
    ll_no_list = []

    for single_elem in input_list:
        if '-' in single_elem:
            start_ll, end_ll = map(int, single_elem.split('-'))
            ll_no_list.extend(range(start_ll, end_ll + 1))
        else:
            ll_no_list.append(int(single_elem))

    return set(ll_no_list)


def upload_ll_batch(con):
    exl_path = filedialog.askopenfilename(initialdir='./', title='Select A Long List File',
                                          filetypes=(("xlsx files", "*.xlsx"), ("all files", "*.*")))

    year = next((str(year_tryout)
    for year_tryout in range(2010, 3000) if str(year_tryout) in exl_path), None)

    if year is None:
        raise ValueError("Could not determine year from file name. Please check the file naming convention.")

    print(f'Year {year} long list is used...')

    inp_str = get_input_list()
    ll_no_set = parse_input_list(inp_str)

    for single_ll in ll_no_set:
        try:
            upload_single_ll(con, exl_path=exl_path, ll_no=single_ll, year=year)
        except Exception as e:
            if 'unique constraint' in str(e):
                print(f'Repeat entry of {single_ll}, this input is ignored...')
            else:
                print(f'Unexpected error when uploading {single_ll}...')
                print(traceback.format_exc())

upload_ll_batch(con=CON)
