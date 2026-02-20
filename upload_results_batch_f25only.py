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
from datetime import datetime

import numpy as np

from log_config import get_logger
logger = get_logger('upload_results_batch')

################################## Utils ##################################
def delete_rows(con, tablename, id, verbose=1):
    delstr = "DELETE FROM "+str(tablename)+" WHERE LONGLIST_ID = "+str(id)
    cursor = con.cursor()
    cursor.execute(delstr)
    con.commit()
    cursor.close()
    if verbose == 1:
        logger.info("Removed illegal entries from %s with id %s", tablename, str(id))

################################## Major function definition ##################################
def upload_single_result(args, f25_path, ll_no, year, con, user_input_dict, commit=0):
    """
    Major function responsible for processing the raw FWD and uploading the calculated resutls to Oracle database.
    This function itself calls many other cutomized functions. Please go through the cutomized functions to gain deeper understanding of how it works.
    """

    mde_path = f25_path[:-3] + 'mde'
    
    if not args.pavtype_special_case:
        # Decide Pavement type automatically using the elastic modulus.
        e1,e2= read_pavtype(mde_path, f25_path)
        # 2000 is the threshold for concrete
        if e1 >= 2000:
            pavtype = 'concrete'
        elif e2 >= 2000:
            pavtype = 'composite'
        else:
            pavtype = 'asphalt'
    elif args.pavtype_special_case:
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
        #### (End) Tkinter code to take user input

    # Preset id to none to prevent termination of batch uploading due to "id cannot find" error
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

    if not (pavtype in ["asphalt", "concrete", "composite"]):
        raise Exception("Please input valid pavement type")
    
    # Assign the new pavement type
    ll_obj['pavtype'] = pavtype

    # print('before ll_query')

    id,dir,lane_type = ll_query(con, ll_no, f25_path, year, start_gps, end_gps, pavtype, args, user_input_dict, commit=1)
    
    ll_obj['dir'] = dir

    mde = None
    calc_data = None
    stats_data = None

    pcc_mod = None
    rxn_subg = None

    mde, roadtype, roadname, ll_obj = read_mde(con, mde_path, f25_path, id, ll_obj, gpsx, gpsy, gpsx_dict, gpsy_dict, args)
    ll_obj["roadname"] = roadname

    calc_data, stats_data, mde, pcc_mod, rxn_subg = calc(con, id, pavtype, roadtype, ll_obj, mde, args)

    if commit:
        db.putmde(con, mde, stats_data, id, commit=1)

    if commit:
        if not args.skip_img_matching:
            db.putimg(con, ll_obj, id, year, lane_type, commit=1)

    if(commit):
        db.putcalc(con, calc_data, id, pcc_mod, rxn_subg)
        db.putstats(con, stats_data, id)

    logger.info('Report generation: %s', args.gen_report)

    if args.gen_report:
        report.gen_report(ll_obj, mde, calc_data, stats_data, mde_path, f25_path, ll_no, year, con, args)

if __name__ == "__main__":
    
    from pathlib import Path
    import argparse

    ############## (Args input, start) ###################
    parser = argparse.ArgumentParser(description='Upload result in batch mode')
    parser.add_argument('--gen_report', action='store_true', help="Use this flag to generate Word report.")
    parser.add_argument('--pavtype_special_case', action='store_true', help="Use this flag if the pavement type cannot be determined correctly through 'read_pavtype' function")
    parser.add_argument('--server_root', type=str, default="\\\\dotwebp016vw/data/FWD/", help="Default image storage location for INDOT image server. Need to change it for local developement.")
    parser.add_argument('--dev_env', type=str, default="shin",choices=['dev_wen', 'shin', 'ecn_wen','ecn_shin'], 
                        help="Use different configs to connect to database. See db.connect for more details.")
    parser.add_argument('--skip_img_matching', action='store_true', help = "If the user does not want to upload images, it has the option to skip it. The code can also skip image matching when there is no image folders")
    parser.add_argument('--txt_path', type=str, help = "path of txt where each line contains a single F25 path. If use this flag, dont use the --gui flag")
    parser.add_argument('--gui', action='store_true', help = "This is for use that want to use a GUI to pick the path of txt that contains multiple F25 paths. If use this flag, dont use the --txt_path flag")
    parser.add_argument('--user_input', action='store_true', help= "Override the automatic LL NO, Year, Test Direction, and Lane Type detection when the F25 path does not follow pre-specific folder structure.")
    args = parser.parse_args()
    ############## (Args input, end) ###################

    ############### (Begin) Tkinter code to take user input for F25 path ###############
    if args.gui:
        txt_path = filedialog.askopenfilename(initialdir='./',title='Select An External .txt File', 
                                            filetypes=(("TXT files","*.txt"),("all files","*.*"))
                                            )
    else:
        txt_path = args.txt_path
    logger.info('txt path: %s', txt_path)
    ############### (End) Tkinter code to take user input for F25 path ###############

    #### Prepare the error log file
    err_log_dir = os.path.dirname(txt_path)
    input_txt_filename = os.path.basename(txt_path)[:-4]
    error_log_file = input_txt_filename +"_error_log.txt"
    warn_log_file = input_txt_filename +"_warn_log.txt"
    filename_error_log_file = input_txt_filename +"_filename_error_log.txt"
    log_error_file_path = os.path.join(err_log_dir,error_log_file)
    warn_log_file_path = os.path.join(err_log_dir,warn_log_file)
    filename_error_log_path = os.path.join(err_log_dir,filename_error_log_file)
    logger.info('Error log is saved in: %s', log_error_file_path)
    if os.path.exists(log_error_file_path):
        logger.info('Overwrite previous error log!!!')
        os.remove(log_error_file_path)
    if os.path.exists(warn_log_file_path):
        os.remove(warn_log_file_path)
    if os.path.exists(filename_error_log_path):
        os.remove(filename_error_log_path)

    logger.info("=" * 60)
    logger.info("RUN STARTED: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("txt_path: %s", txt_path)
    logger.info("args: %s", vars(args))

    # Connect to database. "con" is a object instance, which methods and classes including "cursor" class.
    # "cursor" class can be invoked to upload calculated results to  Oracle database.
    # "con" is called in other functions to upload data to Oracle database.
    logger.info("Connecting to Oracle database (dev_env=%s)...", args.dev_env)
    con = db.connect(args.dev_env)
    logger.info("Oracle connected OK")

    # Reads the txt file where each line is a F25 path.
    with open(txt_path,'r') as file:
        Lines = file.readlines()
    logger.info("Read %d lines from txt file", len(Lines))

    error_flag = False
    for line_idx, line in enumerate(Lines):
        # Automatically detect year, and request number from the file path
        # File path needs to follow the folder structure!!!!!!!!!!
        if not args.user_input:
            split_temp = line.strip().split('\\')
            # match 2 digits after "D" in request number to extract the year 
            year_temp = re.findall(r'D(\d{2})', split_temp[-3])
            if not len(year_temp)==1:
                raise Exception('Something went wrong when extracting the year number from request ID')
            year_2digits_str = year_temp[0]
            f25_path, year = line, int('20'+year_2digits_str)
            f25_path = f25_path.replace('"', '').strip()
            # extract Request NO., and remove the white space
            req_no = split_temp[-3].replace(" ", "")
            ll_no = find_ll_no_given_req_no(con, os.path.basename(f25_path), req_no)
            logger.info("[%d/%d] Processing: %s (LL-%s, year=%s, req=%s)",
                        line_idx+1, len(Lines), os.path.basename(f25_path), ll_no, year, req_no)

        # This is for user input in case of special case like airport test
        else:
            ########### User input interface implemented with Tkinter (Start) ###########
            # Customized input includes LongList Number, Test Direction, Year and Lane Type
            user_input_dict = {}
            f25_path = line
            f25_path = f25_path.replace('"', '').strip()         

            def validate_input():
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
            test_direction_entry = tk.Entry(root)
            test_direction_entry.grid(row=5, column=1)

            # Create a button to submit the form
            submit_button = tk.Button(root, text="Submit", command=validate_input_and_close)
            submit_button.grid(row=6, column=0, columnspan=2)
            root.bind("<Return>", lambda x: validate_input_and_close())

            # Start the main loop
            root.mainloop()
            root.destroy()
            ########### User input interface implemented with Tkinter (End) ###########

            # Extract the LongList Number, Request Number and Year from user input
            ll_no = user_input_dict['ll_no']
            year = user_input_dict['year']
            req_no = find_req_no_given_ll_no(con, os.path.basename(f25_path), ll_no, year)

        # This is the major function that is responsible for calculating and uploading the results.
        # This major function itself will use many other customized functions.
        # Use try and except structure to handle error during excuting "upload_single_result".
        # Try and except used because we want to skip the problematic F25 and MDE files.
        # The bug related to problematic F25 and MDE files will be recorded in the error log file.
        try:
            logger.info("  upload_single_result starting...")
            upload_single_result(args, f25_path, ll_no, year, con, user_input_dict, commit=1)
            logger.info("  upload_single_result completed OK")
        # Roll Back Mechanism: If error occurs in the "upload_single_result" function,
        #                      record the error message in error log file and delete the corresponding row that has been uploaded.
        # Do not delete the corresponding row in the STDA_LONGLIST_INFO,
        # because we don't want to delete the LL request that has been uploaded by "upload_ll_batch.py".
        except Exception as e:
            error_flag = True
            traceback_str = traceback.format_exc()
            logger.error("  EXCEPTION: %s", str(e))
            logger.error("  %s", traceback_str)
            if 'unique constraint' in traceback_str:
                logger.warning('Repeat entry of %s-%s, this input is ignored...', ll_no, year)
            elif "F25 filename does not meet requirement" in traceback_str:
                with open(filename_error_log_path, "a+") as filename_log_f:
                    print("Following F25 file does not meet the filename requirement, please consider using '--user_input'.",
                          file=filename_log_f)
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
                        logger.warning('Due to unexpected error, LL-%s from year %s is deleted, rolling back...', ll_no, year)
                    print('Due to unexpected error, LL-{} from year {} is deleted...'.format(ll_no,year),file=f)
                    print('(End of error log)#############LL-{} from year {} (Request NO. {})#######################\n\n'.format(ll_no,year,req_no),file=f)

    # Main code finish. Output warning message if there are any problematic F25 and MDE files that produces error during excuting "upload_single_result".
    logger.info("Uploading finished!!!")
    if error_flag:
        logger.warning("Errors encountered during batch process but skipped.")
        logger.warning("Check the error log at: %s", log_error_file_path)
    logger.info("RUN ENDED: %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logger.info("=" * 60)