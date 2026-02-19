import sys
import os
import time

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'

import pyodbc
import pandas as pd

print("=== TEST 1: connect to existing accdb (no copy) ===")
try:
    conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path)
    print("TEST 1: connected OK")
    df = pd.read_sql('select * from Thickness ORDER BY SectionID ASC', conn)
    print("TEST 1: e1=", df['e1'][0], "e2=", df['e2'][0])
    conn.close()
    print("TEST 1: closed OK")
except Exception as e:
    print("TEST 1 FAILED:", e)

print("\n=== TEST 2: connect to mde directly (no copy) ===")
try:
    conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + mde_path)
    print("TEST 2: connected OK")
    df = pd.read_sql('select * from Thickness ORDER BY SectionID ASC', conn)
    print("TEST 2: e1=", df['e1'][0], "e2=", df['e2'][0])
    conn.close()
    print("TEST 2: closed OK")
except Exception as e:
    print("TEST 2 FAILED:", e)

print("\n=== TEST 3: copy mde->accdb then connect ===")
import shutil
try:
    shutil.copy(mde_path, accdb_path)
    print("TEST 3: copy done, waiting 2 seconds...")
    time.sleep(2)
    conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path)
    print("TEST 3: connected OK")
    df = pd.read_sql('select * from Thickness ORDER BY SectionID ASC', conn)
    print("TEST 3: e1=", df['e1'][0], "e2=", df['e2'][0])
    conn.close()
    print("TEST 3: closed OK")
except Exception as e:
    print("TEST 3 FAILED:", e)

print("\n=== TEST 4: copy mde->accdb to TEMP folder then connect ===")
try:
    temp_accdb = os.path.join(os.environ['TEMP'], 'test_underseal.accdb')
    shutil.copy(mde_path, temp_accdb)
    print("TEST 4: copied to", temp_accdb)
    time.sleep(1)
    conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + temp_accdb)
    print("TEST 4: connected OK")
    df = pd.read_sql('select * from Thickness ORDER BY SectionID ASC', conn)
    print("TEST 4: e1=", df['e1'][0], "e2=", df['e2'][0])
    conn.close()
    print("TEST 4: closed OK")
    os.remove(temp_accdb)
except Exception as e:
    print("TEST 4 FAILED:", e)

print("\n=== ALL TESTS DONE ===")
