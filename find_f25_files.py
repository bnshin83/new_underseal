"""
Deprecated script. 

This script was used to get get the pickle file from './unused_var_dict/' using request number get the LL no and year
"""


import os
import pickle as pkl
import re

def extract_f25_filename(con, historical_dir,error_log):
    input_txt = os.path.join(historical_dir,"result_upload_input.txt")
    if os.path.exists(input_txt):
        os.remove(input_txt)
    if os.path.exists(error_log):
        os.remove(error_log)

    for req_no in os.listdir(historical_dir):
        if not os.path.isdir(os.path.join(historical_dir,req_no)):
            continue
        found_flag = False
        sqlstr = """
                 SELECT longlist_no FROM stda_longlist_info
                 WHERE request_no='""" + req_no + """'
                 """
        cursor = con.cursor()
        cursor.execute(sqlstr)
        ll_no = None
        for result in cursor:
            ll_no = result[0]
        cursor.close()
        if not ll_no:
            print('cannot find coresponding req_no {} in DB.'.format(req_no))
        # open pkl file
        pkl_folder = './unused_var_dict/'
        year_2digits_str = re.findall(r'D(\d{2})', req_no)[0]
        year = '20'+year_2digits_str
        pkl_filename = 'LL-{}-{}.pkl'.format(ll_no,year)
        print(pkl_filename)
        pkl_path = os.path.join(pkl_folder, pkl_filename)
        with open(pkl_path,"rb") as f:
            ll_obj = pkl.load(f)['ll_obj']
        route = ll_obj['route']
        RouteAndLLNo = '{} LL-{}'.format(route, ll_no)
        if RouteAndLLNo in os.listdir(os.path.join(historical_dir,req_no)):
            F25AndMDE_folder = os.path.join(historical_dir,req_no,RouteAndLLNo)
            found_flag = True
        else:
            rp_from_temp = ll_obj['rp from'].split(".")
            rp_to_temp = ll_obj['rp to'].split(".")
            # get int and deci part of RP
            rp_from_int = rp_from_temp[0]
            if len(rp_from_temp) == 1:
                rp_from_deci = '00'
            else:
                rp_from_deci = rp_from_temp[1]
                if len(rp_from_deci) == 1:
                    rp_from_deci = rp_from_deci + '0'
            rp_to_int = rp_to_temp[0]
            if len(rp_to_temp) == 1:
                rp_to_deci = '00'
            else:
                rp_to_deci = rp_to_temp[1]
                if len(rp_to_deci)==1:
                    rp_to_deci = rp_to_deci + '0'
            RouteRP = "{} RP-{}+{} to RP-{}+{}".format(route,
                                                       rp_from_int,rp_from_deci,
                                                       rp_to_int, rp_to_deci)
            if RouteRP in os.listdir(os.path.join(historical_dir,req_no)):
                F25AndMDE_folder = os.path.join(historical_dir,req_no,RouteRP)
                found_flag = True
            else:
                with open(error_log,"a+") as f:
                    f.write('#####')
                    f.write("Cant find F25MDE folder for Req. NO. {}. RouteAndLLNo: {} RouteRP: {}".format(req_no,RouteAndLLNo,RouteRP))
                    f.write('#####\n\n')
                # raise Exception("Cant find F25MDE folder for Req. NO. {}. RouteAndLLNo: {} RouteRP: {}".format(req_no,RouteAndLLNo,RouteRP))

        # gather all F25 inside the folder
        if found_flag:
            with open(input_txt,"a+") as output_txt:
                for filename in os.listdir(os.path.join(historical_dir,req_no,F25AndMDE_folder)):
                    if filename.endswith(".F25"):
                        output_txt.write("{}\n".format(os.path.join(historical_dir,req_no,F25AndMDE_folder,filename)))


if __name__=="__main__":

    import db
    from tkinter import filedialog
    import argparse

    parser = argparse.ArgumentParser(description='Upload result in batch mode')
    parser.add_argument('--dev_env', type=str, default="shin",choices=['dev_wen', 'shin', 'ecn_wen','ecn_shin'])
    args = parser.parse_args()

    if args.dev_env in ['dev_wen','ecn_wen']:
        historical_dir = filedialog.askdirectory(initialdir='D:/indot_proj/Underseal/result_folder/historical_data/historical_data/',
                                                title='Select A Year Folder'
                                                )
    else:
        historical_dir = filedialog.askdirectory(initialdir='./',
                                                title='Select A Year Folder'
                                                )
    
    error_log = os.path.join(historical_dir,'find_all_F25_error.txt')

    con = db.connect(args.dev_env)

    extract_f25_filename(con, historical_dir,error_log)

