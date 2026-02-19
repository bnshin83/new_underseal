import pyodbc
import cx_Oracle
import shutil

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'
ACCESS_DSN = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path

print("=== Binary search: which part of ll_query import causes hang ===\n")

# Oracle setup
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
print("Oracle connected")

# Do the query manually
cursor = ora_con.cursor()
cursor.execute("SELECT longlist_no FROM stda_longlist_info WHERE request_no='D2304249032'")
for r in cursor:
    ll_no = str(r[0])
cursor.close()
print("ll_no:", ll_no)

shutil.copy(mde_path, accdb_path)
print("copy done")

# TEST A: just import ll_query (don't call anything)
print("\nTEST A: import ll_query only...")
import ll_query
print("TEST A: imported")
conn = pyodbc.connect(ACCESS_DSN)
print("TEST A: Access connected OK")
conn.close()
print("TEST A: PASSED")

print("\n=== PASSED ===")
