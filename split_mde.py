import pyodbc
# import excel
import msaccessdb
import os
import pandas as pd
import numpy as np
import shutil
import tkinter as tk
from tkinter import *
from tkinter import filedialog

from log_config import get_logger
logger = get_logger('split_mde')

def build_mde():
    # root = tk.Tk()
    # root.update_idletasks()
    mdepath = filedialog.askopenfilename(initialdir='./',title='Select A MDE File', 
                                          filetypes=(("MDE files","*.mde"),("all files","*.*"))
                                         )
    # print(f25_path)
    # mdepath = "D:\\shrey\\Documents\\split mde\\cho.mde"
    pre, ext = os.path.splitext(mdepath)
    newpath = pre + '.accdb'
    shutil.copy(mdepath, newpath)
    driver_str = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + str(newpath)
    mde_conn = pyodbc.connect(driver_str)
    cursor = mde_conn.cursor()
    tables = [i for i in cursor.tables()]
    
    sqlstr = 'SELECT DISTINCT FileName from Deflections'
    filenames = pd.read_sql(sqlstr, mde_conn)
    logger.info("Filenames in MDE:\n%s", filenames)
    files_dict = {}
    for i in range(len(filenames)):
        prefix = str(os.path.split(newpath)[0])
        # if(filenames.loc[i, 'FileName'][-4:] == '_F25'):
        #     print("OH YEAH")
        
        filename = filenames.loc[i, 'FileName']
        if(filename[-4:] == '_F25'):
            filename = filename[0:-4]
        filename = filename.strip()
        createpath = prefix + '\\' + filename + '.mdb'
        files_dict[filenames.loc[i, 'FileName']] = createpath
        delpath = prefix + '\\' + filename + '.mde'
        # msaccessdb.create(createpath)
        if(os.path.exists(delpath)):
            os.remove(delpath)
        shutil.copy(newpath, createpath)
    
    for table in tables:
        # print(table.table_name)
        if table.table_type != 'TABLE':
            continue
        cursor = mde_conn.cursor()
        
        # sqlstr = "SELECT COUNT(*) from (SELECT DISTINCT FILENAME FROM "+str(table.table_name)+")"
        # sqlstr = 'SELECT COUNT(*) from (SELECT DISTINCT FILENAME FROM DEFLECTIONS)'
        # sqlstr = "SELECT * FROM [" + table.table_name + "]"
        sqlstr = 'SELECT * FROM [' + table.table_name + ']'
        df = pd.read_sql(sqlstr, mde_conn)
        if 'FileName' in df.columns:
            for file in files_dict.keys():
                writeToDB(file, files_dict[file], table.table_name, df.loc[df['FileName']==file])
        elif 'Filename' in df.columns:
            for file in files_dict.keys():
                writeToDB(file, files_dict[file], table.table_name, df.loc[df['Filename']==file])
    
    for file in files_dict.keys():
        pre, ext = os.path.splitext(files_dict[file])
        newpath = pre + '.mde'
        shutil.move(files_dict[file], newpath)

    




def writeToDB(key, filepath, table_name, df):
    driver_str = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + filepath
    mde_conn = pyodbc.connect(driver_str)
       
    # sqlstr = "DELETE FROM ["+table_name+"] WHERE FileName <> '"+key+"' OR Filename <>'"+key+"'"
    sqlstr = "DELETE FROM ["+table_name+"] WHERE Filename <>'"+key+"'"
    
    cursor = mde_conn.cursor()
    result = cursor.execute(sqlstr)
    cursor.commit()

    
    

    # print(driver_str)
    
    # print(df.info())
    # print("Writing to table_name: ", table_name)
    # print(df)
    # df.to_sql(table_name, mde_conn, if_exists="replace")
    

    
            


build_mde()
    