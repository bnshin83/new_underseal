import sys
import os

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'

print("=== DIAGNOSTIC START ===")
print("Python:", sys.version)

# Check pyodbc
print("\n--- pyodbc ---")
import pyodbc
print("pyodbc version:", pyodbc.version)
print("Access drivers:", [d for d in pyodbc.drivers() if 'Access' in d])

# Check for lock files
print("\n--- Lock files ---")
lock_path = accdb_path.replace('.accdb', '.laccdb')
print("Lock file exists:", os.path.exists(lock_path))
if os.path.exists(lock_path):
    print("WARNING: lock file found! Another process may have the file open.")

# Check file exists
print("\n--- Files ---")
print("accdb exists:", os.path.exists(accdb_path))
print("mde exists:", os.path.exists(mde_path))

# Check pandas
print("\n--- pandas ---")
import pandas as pd
print("pandas version:", pd.__version__)

# Check numpy
import numpy as np
print("numpy version:", np.__version__)

# Test shutil.copy (what read_pavtype does first)
print("\n--- shutil.copy mde->accdb ---")
import shutil
try:
    shutil.copy(mde_path, accdb_path)
    print("copy OK, size:", os.path.getsize(accdb_path))
except Exception as e:
    print("copy FAILED:", e)

# Test connection
print("\n--- pyodbc.connect ---")
try:
    driver_str = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path
    print("connecting with:", driver_str[:80], "...")
    conn = pyodbc.connect(driver_str)
    print("connected OK")
except Exception as e:
    print("connect FAILED:", e)
    print("=== DIAGNOSTIC END (failed at connect) ===")
    sys.exit(1)

# Test query
print("\n--- SQL query ---")
try:
    df = pd.read_sql('select * from Thickness ORDER BY SectionID ASC', conn)
    print("query OK, rows:", len(df))
    print("e1=", df['e1'][0], "e2=", df['e2'][0])
except Exception as e:
    print("query FAILED:", e)

# Close
conn.close()
print("\n=== DIAGNOSTIC END (all passed) ===")
