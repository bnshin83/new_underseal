import pyodbc
import cx_Oracle
import shutil
import os

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'
ACCESS_DSN = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path

print("=== Test: using actual find_ll_no_given_req_no ===\n")

# Oracle setup
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
print("Oracle connected OK")

# Use the ACTUAL function from ll_query
from ll_query import find_ll_no_given_req_no
print("imported find_ll_no_given_req_no")

ll_no = find_ll_no_given_req_no(ora_con, 'US-31 NB RP-128+36 to RP-129+29 LN 3.F25', 'D2304249032')
print("ll_no:", ll_no)

# Now try Access
shutil.copy(mde_path, accdb_path)
print("copy done")

print("About to pyodbc.connect...")
conn = pyodbc.connect(ACCESS_DSN)
print("Access connected OK")
conn.close()

ora_con.close()
print("=== PASSED ===")
