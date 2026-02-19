import sys
import pyodbc
import cx_Oracle
import shutil
import os

# Import everything the main script imports
import db
from ll_query import find_ll_no_given_req_no
from mde_entry import read_mde, getGPS, read_pavtype
from calculate import calc
import report

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'

print("=== Test subprocess fix ===\n")

print("Step 1: Oracle connect...")
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
print("Step 1: OK")

print("\nStep 2: Oracle query...")
ll_no = find_ll_no_given_req_no(ora_con, 'test.F25', 'D2304249032')
print("Step 2: ll_no =", ll_no)

print("\nStep 3: read_pavtype (subprocess Access)...")
e1, e2 = read_pavtype(mde_path, r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.F25')
print("Step 3: e1={}, e2={}".format(e1, e2))

ora_con.close()
print("\n=== ALL PASSED ===")
