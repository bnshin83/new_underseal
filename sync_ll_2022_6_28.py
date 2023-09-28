# This file is used to check and synchonize all the rows that have been uploaded to the Long List Database
# Change 2022 "long List" to "Long List Number"
# Change 2022 "Comments by requestor \n (priority)" to "Comments by requestor (priority)"
# Change 2022 "status" to "Status"
# Need to add "Pavement Type" column

import db
import excel

from query_db import read_db, update_db, get_unique_ll_no_list

import warnings
warnings.filterwarnings("ignore")

def check_single_ll(con, ll_no, year, excel_path):
    excel_row_dict = {}
    db_dict= {}

    result_list = read_db(con,
                          table_name='stda_longlist_info',
                          col_name='traffic_ctrl, operator, operator_comment, test_status',
                          cond_name='longlist_no',
                          cond_value=ll_no,
                          year=year)
    db_dict['traffic_ctrl'] = result_list[0]
    db_dict['operator'] = result_list[1]
    db_dict['operator_comment'] = result_list[2]
    db_dict['test_status'] = result_list[3]

    excel_row = excel.return_ll_info_row(excel_path,ll_no,"Test Request Overview")
    excel_row_dict['traffic_ctrl'] = str(excel.return_value(excel_row,'Traffic Control Scheduled (Put only single day)'))
    excel_row_dict['operator'] = str(excel.return_value(excel_row,'Operator'))
    excel_row_dict['operator_comment'] = str(excel.return_value(excel_row,'Operator comments'))
    excel_row_dict['test_status'] = str(excel.return_value(excel_row,'Status'))

    # Open a new cursor here
    cursor = con.cursor()
    for key_name in excel_row_dict.keys():
        if excel_row_dict[key_name] != db_dict[key_name]:
            print(ll_no)
            update_db(con,
                      table_name="stda_longlist_info",
                      update_col=key_name,
                      new_value=excel_row_dict[key_name],
                      ll_no=ll_no,
                      year=year)

    con.commit()
    cursor.close()
    
if __name__=='__main__':
    from tkinter import *
    from tkinter import filedialog, simpledialog
    import argparse

    parser = argparse.ArgumentParser(description='Upload result in batch mode')
    parser.add_argument('--dev_env', type=str, default="shin",choices=['dev_wen', 'shin', 'ecn_wen','ecn_shin'])
    args = parser.parse_args()

    root = Tk()
    root.focus_force()
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

    # #### (Begin) Tkinter code to take user input
    # def get_inp_year(event):
    #     global year
    #     year = myEntry.get()
    #     root.quit()
    
    # root= Tk()
    # Label(root, text="Input the year to synchronize the longlist table.", font=('Calibri 10')).pack()
    # myEntry = Entry(root)
    # myEntry.focus_force()
    # myEntry.pack()
    # Button(root,text='OK',command=get_inp_year).pack(pady=10)
    # root.bind('<Return>', get_inp_year)
    # root.mainloop()
    # #### (End) Tkinter code to take user input

    ## The data type for year is now string instead of int!!!!!!!
    root.focus_force()
    print('Sync year:',year)
    CON = db.connect(args.dev_env)
    ll_no_list = get_unique_ll_no_list(CON,year)
    for ll_no in ll_no_list:
        check_single_ll(CON, ll_no, year, exl_path)
