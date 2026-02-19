import pyodbc
import cx_Oracle
import shutil
import db
import excel
import os, re

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'
ACCESS_DSN = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path

print("=== Test: exact same imports as upload_results_batch_f25only ===\n")

# Import everything the main script imports at the top
print("Importing all modules the main script imports...")
from ll_query import ll_query
from mde_entry import read_mde, getGPS, read_pavtype
from calculate import calc
import report
from ll_query import get_ll_obj, find_ll_no_given_req_no, find_req_no_given_ll_no
import pickle as pkl
import warnings
warnings.filterwarnings("ignore")
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import traceback
import numpy as np
print("All imports done")

# Oracle
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
print("Oracle connected")

# Query
ll_no = find_ll_no_given_req_no(ora_con, 'US-31 NB RP-128+36 to RP-129+29 LN 3.F25', 'D2304249032')
print("ll_no:", ll_no)

# Copy + Access
shutil.copy(mde_path, accdb_path)
print("copy done")

print("About to Access connect...")
conn = pyodbc.connect(ACCESS_DSN)
print("Access connected OK")
conn.close()

ora_con.close()
print("\n=== PASSED ===")
