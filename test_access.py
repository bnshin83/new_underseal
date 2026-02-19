import pyodbc
import cx_Oracle
import shutil
import os
import re
import pandas as pd

# Simulate exactly what the script does step by step

print("=== Simulating exact script flow ===\n")

# Step 1: Oracle connect (same as script line 181)
print("STEP 1: Oracle init + connect...")
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
print("STEP 1: Oracle connected OK")

# Step 2: Read file (same as script line 184-185)
txt_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\ML_ 10.75_ Concrete; SH_ 5.25_ HMA.txt'
print("\nSTEP 2: Reading txt file...")
with open(txt_path, 'r') as file:
    Lines = file.readlines()
print("STEP 2: Read", len(Lines), "lines")
print("STEP 2: First line:", Lines[0].strip())

# Step 3: Parse path (same as script lines 196-206)
line = Lines[0]
print("\nSTEP 3: Parsing path...")
split_temp = line.strip().split('\\')
print("STEP 3: split_temp[-3]:", split_temp[-3])
year_temp = re.findall(r'D(\d{2})', split_temp[-3])
year_2digits_str = year_temp[0]
f25_path = line.replace('"', '').strip()
year = int('20' + year_2digits_str)
req_no = split_temp[-3].replace(" ", "")
print("STEP 3: f25_path:", f25_path)
print("STEP 3: year:", year, "req_no:", req_no)

# Step 4: Oracle query (find_ll_no_given_req_no)
print("\nSTEP 4: Oracle query for ll_no...")
cursor = ora_con.cursor()
cursor.execute("SELECT LL_NO FROM STDA_LONGLIST_INFO WHERE REQUEST_NO = :1", [req_no])
row = cursor.fetchone()
if row:
    print("STEP 4: ll_no from query:", row[0])
cursor.close()
print("STEP 4: Oracle cursor closed")

# Step 5: This is read_pavtype - the exact function that hangs
mde_path = f25_path[:-3] + 'mde'
accdb_path = f25_path[:-3] + 'accdb'
print("\nSTEP 5a: shutil.copy mde->accdb...")
print("  from:", mde_path)
print("  to:", accdb_path)

# Check for lock file before copy
lock_path = accdb_path.replace('.accdb', '.laccdb')
print("  lock file exists before copy:", os.path.exists(lock_path))

shutil.copy(mde_path, accdb_path)
print("STEP 5a: copy done, size:", os.path.getsize(accdb_path))

# Check for lock file after copy
print("  lock file exists after copy:", os.path.exists(lock_path))

print("\nSTEP 5b: pyodbc.connect to accdb...")
driver_str = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + str(accdb_path)
print("  driver_str:", driver_str)
access_conn = pyodbc.connect(driver_str)
print("STEP 5b: Access connected OK")

df = pd.read_sql('select * from Thickness ORDER BY SectionID ASC', access_conn)
print("STEP 5c: e1=", df['e1'][0], "e2=", df['e2'][0])
access_conn.close()
print("STEP 5c: Access closed OK")

ora_con.close()
print("\n=== ALL STEPS PASSED ===")
