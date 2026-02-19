import pyodbc
import cx_Oracle
import shutil
import os

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'
ACCESS_DSN = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path

print("=== Narrowing down: Oracle cursor + Access ===\n")

# Oracle setup
print("STEP 1: Oracle init + connect...")
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
print("STEP 1: OK")

# Test A: Access before any Oracle query
print("\nTEST A: Access connect before any Oracle query...")
conn = pyodbc.connect(ACCESS_DSN)
print("TEST A: OK")
conn.close()

# Test B: Simple Oracle query, cursor closed
print("\nTEST B: Oracle query (cursor open+close)...")
cursor = ora_con.cursor()
cursor.execute("SELECT 1 FROM DUAL")
row = cursor.fetchone()
print("TEST B: query result:", row[0])
cursor.close()
print("TEST B: cursor closed")

print("\nTEST B2: Access connect after simple Oracle query...")
conn = pyodbc.connect(ACCESS_DSN)
print("TEST B2: OK")
conn.close()

# Test C: Actual find_ll_no query
print("\nTEST C: Actual stda_longlist_info query...")
cursor = ora_con.cursor()
cursor.execute("SELECT longlist_no FROM stda_longlist_info WHERE request_no='D2304249032'")
for result in cursor:
    print("TEST C: ll_no =", result[0])
cursor.close()
print("TEST C: cursor closed")

print("\nTEST C2: Access connect after stda query...")
conn = pyodbc.connect(ACCESS_DSN)
print("TEST C2: OK")
conn.close()

# Test D: Copy mde->accdb THEN Access connect (after Oracle queries)
print("\nTEST D: shutil.copy mde->accdb...")
shutil.copy(mde_path, accdb_path)
print("TEST D: copy done")

print("\nTEST D2: Access connect after copy + Oracle queries...")
conn = pyodbc.connect(ACCESS_DSN)
print("TEST D2: OK")
conn.close()

ora_con.close()
print("\n=== ALL PASSED ===")
