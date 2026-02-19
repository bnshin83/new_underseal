import pyodbc
import cx_Oracle
import shutil

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'
ACCESS_DSN = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path

print("=== Test: replicate ll_query imports without importing ll_query ===\n")

cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
print("Oracle connected")

cursor = ora_con.cursor()
cursor.execute("SELECT longlist_no FROM stda_longlist_info WHERE request_no='D2304249032'")
for r in cursor:
    ll_no = str(r[0])
cursor.close()
print("ll_no:", ll_no)

shutil.copy(mde_path, accdb_path)
print("copy done")

# ll_query.py imports: pyodbc, cx_Oracle, db, excel, os, re
# Try importing them one at a time and test Access after each

print("\nA: import pyodbc (already imported)...")
import pyodbc
conn = pyodbc.connect(ACCESS_DSN); conn.close()
print("A: OK")

print("\nB: import cx_Oracle (already imported)...")
import cx_Oracle
conn = pyodbc.connect(ACCESS_DSN); conn.close()
print("B: OK")

print("\nC: import db...")
import db
conn = pyodbc.connect(ACCESS_DSN); conn.close()
print("C: OK")

print("\nD: import excel...")
import excel
conn = pyodbc.connect(ACCESS_DSN); conn.close()
print("D: OK")

print("\nE: import os, re...")
import os, re
conn = pyodbc.connect(ACCESS_DSN); conn.close()
print("E: OK")

print("\nF: now import ll_query itself...")
import ll_query
conn = pyodbc.connect(ACCESS_DSN); conn.close()
print("F: OK")

ora_con.close()
print("\n=== ALL PASSED ===")
