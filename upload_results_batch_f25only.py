import db
from ll_query import ll_query
from mde_entry import read_mde, getGPS, read_pavtype
from calculate import calc

import report

from ll_query import get_ll_obj, find_ll_no_given_req_no, find_req_no_given_ll_no
# from writefiles import writeELMOD_FWD, writeLCC, writeLCC0, writeLCC1
# from match_calc import match
import pickle as pkl
import os, sys
import warnings
warnings.filterwarnings("ignore")

import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

import traceback, re

import numpy as np

################################## Utils ##################################
def delete_rows(con, tablename, id, verbose=1):
    delstr = "DELETE FROM "+str(tablename)+" WHERE LONGLIST_ID = "+str(id)
    cursor = con.cursor()
    cursor.execute(delstr)
    con.commit()
    cursor.close()
    if verbose == 1:
        print("Removed illegal entries from ", tablename, "with id ", str(id))

################################## Main ##################################
def upload_single_result(args, f25_path, ll_no, year, con, user_input_dict, commit=0):

    mde_path = f25_path[:-3] + 'mde'
    
    if not args.special_case and not args.user_input:
        # Decide Pavement type
        e1,e2= read_pavtype(mde_path, f25_path)
        # 2000 is the threshold for concrete
        if e1 >= 2000:
            pavtype = 'concrete'
        elif e2 >= 2000:
            pavtype = 'composite'
        else:
            pavtype = 'asphalt'
    elif args.special_case:
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
    # Preset id to none to prevent exit of batch uploading due to "id cannot find" error
    global id
    id = None

    # retrive ll_obj from database
    ll_obj = get_ll_obj(con, ll_no, year)

    # Extract Start and End GPS
    gpsx, gpsy, gpsx_dict, gpsy_dict = getGPS(f25_path)
    if len(gpsx)>0 and len(gpsy)>0:
        start_gps, end_gps = (gpsx[0], gpsy[0]), (gpsx[-1], gpsy[-1])
    else:
        start_gps, end_gps = None, None

    if args.user_input:
        pavtype = user_input_dict['pavtype']
    if not (pavtype in ["asphalt", "concrete", "composite"]):
        raise Exception("Please input valid pavement type")
    # Assign the new pavement type
    ll_obj['pavtype'] = pavtype

    if args.debug:
        id,dir, lane_type = ll_query(con, ll_no, f25_path, year, start_gps, end_gps, pavtype, args, user_input_dict, commit=0)
    else:
        id,dir,lane_type = ll_query(con, ll_no, f25_path, year, start_gps, end_gps, pavtype, args, user_input_dict, commit=1) # change to commit=1 when in production
    
    ll_obj['dir'] = dir

    mde = None
    calc_data = None
    stats_data = None

    pcc_mod = None
    rxn_subg = None

    mde, roadtype, roadname, ll_obj = read_mde(con, mde_path, f25_path, id, ll_obj, gpsx, gpsy, gpsx_dict, gpsy_dict, args.server_root, args.skip_img_matching)
    ll_obj["roadname"] = roadname

    calc_data, stats_data, mde, pcc_mod, rxn_subg = calc(con, id, pavtype, roadtype, ll_obj, mde, args.special_case)

    if commit:
        db.putmde(con, mde, stats_data, id, commit=1)

    if commit:
        if not args.skip_img_matching:
            db.putimg(con, ll_obj, id, year, lane_type, commit=1)

    if(commit):
        db.putcalc(con, calc_data, id, pcc_mod, rxn_subg)
        db.putstats(con, stats_data, id)

    print('Report generation: ', args.gen_report)

    if args.gen_report:
        report.gen_report(ll_obj, mde, calc_data, stats_data, mde_path, f25_path, ll_no, year, con, args.special_case)


    if args.user_input:
        return user_input_dict
    else:
        return None

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
    parser.add_argument('--txt_path', type=str)
    parser.add_argument('--gui', action='store_true')
    parser.add_argument('--user_input', action='store_true')
    args = parser.parse_args()

    ### (Begin) Tkinter code to take user input
    if args.gui:
        if args.dev_env != 'dev_wen':
            txt_path = filedialog.askopenfilename(initialdir='./',title='Select An External .txt File', 
                                                filetypes=(("TXT files","*.txt"),("all files","*.*"))
                                                )
        else:
            txt_path = filedialog.askopenfilename(initialdir='D:/indot_proj/Underseal/result_folder/', title='Select An External .txt File', 
                                                filetypes=(("TXT files","*.txt"),("all files","*.*"))
                                                )
    else:
        txt_path = args.txt_path
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
        
    for line in Lines:
        # This is for user input in case of special case like airport test 
        user_input_dict = {}
        if not args.user_input:
            split_temp = line.strip().split('\\')
            # match 2 digits after "D" in request number to extract the year 
            year_temp = re.findall(r'D(\d{2})', split_temp[-3])
            if not len(year_temp)==1:
                raise Exception('Something went wrong when extracting the year number from request ID')
            year_2digits_str = year_temp[0]
            f25_path, year = line, int('20'+year_2digits_str)
            f25_path = f25_path.replace('"', '').strip()
            # Extract the ll_no using regex (not using any more)
            # ll_no_temp = re.findall(r'LL\s?-?\s?(\d+)', split_temp[-2])
            # extract Request NO., and remove the white space
            req_no = split_temp[-3].replace(" ", "")
            ll_no = find_ll_no_given_req_no(con, os.path.basename(f25_path), req_no)
        else:
            f25_path = line
            f25_path = f25_path.replace('"', '').strip()         

            def validate_input():
                if not pavement_type_combobox.get().strip():
                    show_error("Please select a pavement type.")
                    return False
                if pavement_type_combobox.get().strip() not in ["asphalt", "concrete", "composite"]:
                    show_error("Pavement type must be chosen from 'asphalt', 'concrete', or 'composite'")
                    return False
                if not long_list_number_entry.get():
                    show_error("Please enter the Request Number.")
                    return False
                if not test_direction_entry.get():
                    show_error("Please enter the Test Direction.")
                    return False
                if not year_entry.get():
                    show_error("Please enter the Year.")
                    return False
                if not lane_type_entry.get():
                    show_error("Please enter the Lane Type.")
                    return False
                return True

            def show_error(message):
                messagebox.showerror("Error", message)

            def validate_input_and_close():
                if validate_input():
                    # Collect input and close window
                    user_input_dict['pavtype'] = pavement_type_combobox.get().strip()
                    user_input_dict['ll_no'] = long_list_number_entry.get().strip()
                    user_input_dict['dir'] = test_direction_entry.get().strip()
                    user_input_dict['year'] = year_entry.get().strip()
                    user_input_dict['lane_type'] = lane_type_entry.get().strip()
                    root.quit()

            root = tk.Tk()
            root.title("Please Enter information manully")
            root.geometry("400x400")
            root.grid_rowconfigure(0, minsize=40)
            root.grid_rowconfigure(1, minsize=40)
            root.grid_rowconfigure(2, minsize=40)
            root.grid_rowconfigure(3, minsize=40)
            root.grid_rowconfigure(4, minsize=40)
            root.grid_rowconfigure(5, minsize=40)
            root.grid_rowconfigure(6, minsize=40)
            root.grid_rowconfigure(7, minsize=40)

            root.columnconfigure(0, weight=1)  # Make column 0 flexible
            root.columnconfigure(1, weight=2)  # Make column 1 flexible

            root.update_idletasks()

            spacer = tk.Label(root, height=2)  # Adjust the height as needed
            spacer.grid(row=1, column=0, columnspan=2)

            cur_file_line = tk.Label(root, text='Current file: \n {}'.format(os.path.basename(f25_path)))  # Adjust the height as needed
            cur_file_line.grid(row=1, column=0, columnspan=2)

            long_list_number_label = tk.Label(root, text="Long List Number:")
            long_list_number_label.grid(row=2, column=0)
            long_list_number_entry = tk.Entry(root)
            long_list_number_entry.grid(row=2, column=1)

            year_label = tk.Label(root, text="Year:")
            year_label.grid(row=3, column=0)
            year_entry = tk.Entry(root)
            year_entry.grid(row=3, column=1)

            lane_type_label = tk.Label(root, text="Lane Type:")
            lane_type_label.grid(row=4, column=0)
            lane_type_entry = tk.Entry(root)
            lane_type_entry.grid(row=4, column=1)
            
            test_direction_label = tk.Label(root, text="Test Direction:")
            test_direction_label.grid(row=5, column=0)
            test_direction_entry = ttk.Combobox(root, values=["NB", "SB", "EB", "WB"])
            test_direction_entry.grid(row=5, column=1)

            pavement_type_label = tk.Label(root, text="Choose the pavement type")
            pavement_type_label.grid(row=6, column=0)
            pavement_type_combobox = ttk.Combobox(root, values=["asphalt", "concrete", "composite"])
            pavement_type_combobox.grid(row=6, column=1)

            # Create a button to submit the form
            submit_button = tk.Button(root, text="Submit", command=validate_input_and_close)
            submit_button.grid(row=7, column=0, columnspan=2)
            root.bind("<Return>", lambda x: validate_input_and_close())

            # Start the main loop
            root.mainloop()
            root.destroy()

            ll_no = user_input_dict['ll_no']
            year = user_input_dict['year']
            pavtype = user_input_dict['pavtype']
            req_no = find_req_no_given_ll_no(con, os.path.basename(f25_path), ll_no, year)

        try:
            if args.debug:
                upload_single_result(args, f25_path, ll_no, year, con, user_input_dict, commit=0)
            else:
                upload_single_result(args, f25_path, ll_no, year, con, user_input_dict, commit=1) # change to commit=1 when in production
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

    print("\n Uploading finished!!!")