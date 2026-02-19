import pyodbc
import cx_Oracle
import shutil
import db
import excel
import os, re

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'
ACCESS_DSN = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path

cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")

from ll_query import find_ll_no_given_req_no
ll_no = find_ll_no_given_req_no(ora_con, 'test.F25', 'D2304249032')
print("ll_no:", ll_no)
shutil.copy(mde_path, accdb_path)

print("=== Which import breaks it? ===\n")

print("A: from mde_entry import read_mde, getGPS, read_pavtype...")
from mde_entry import read_mde, getGPS, read_pavtype
conn = pyodbc.connect(ACCESS_DSN); conn.close()
print("A: OK")

print("\nB: from calculate import calc...")
from calculate import calc
conn = pyodbc.connect(ACCESS_DSN); conn.close()
print("B: OK")

print("\nC: import report...")
import report
conn = pyodbc.connect(ACCESS_DSN); conn.close()
print("C: OK")

ora_con.close()
print("\n=== ALL PASSED ===")
