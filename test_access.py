import os
import sys

print("=== Verify fix and test ===\n")

# Check git status
print("Step 0: Verify files")
print("  Current branch check - look at match_images.py line 3:")

# Read match_images.py line 3 to see if PIL import is removed
with open("match_images.py", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:10]):
        print("  line {}: {}".format(i+1, line.rstrip()))

has_pil_top = any("from PIL import Image" in line for line in lines[:5])
print("\n  PIL at top level:", has_pil_top)
if has_pil_top:
    print("  WARNING: Fix not applied! PIL still imported at top of match_images.py")
    print("  Run: git pull")
    sys.exit(1)
else:
    print("  Good - PIL not at top level")

# Now do the actual test
import pyodbc
import cx_Oracle
import shutil

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'
ACCESS_DSN = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path

print("\nStep 1: import mde_entry (should NOT load PIL now)...")
from mde_entry import read_mde, getGPS, read_pavtype
print("Step 1: OK")

# Check if PIL is loaded
pil_loaded = 'PIL' in sys.modules or 'PIL.Image' in sys.modules
print("  PIL loaded in memory:", pil_loaded)

print("\nStep 2: Oracle connect...")
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
print("Step 2: OK")

print("\nStep 3: Oracle query...")
from ll_query import find_ll_no_given_req_no
ll_no = find_ll_no_given_req_no(ora_con, 'test.F25', 'D2304249032')
print("Step 3: ll_no =", ll_no)

print("\nStep 4: copy mde->accdb...")
shutil.copy(mde_path, accdb_path)
print("Step 4: OK")

print("\nStep 5: Access connect (the one that was hanging)...")
conn = pyodbc.connect(ACCESS_DSN)
print("Step 5: Access connected OK!")
conn.close()

ora_con.close()
print("\n=== FIX VERIFIED - ALL PASSED ===")
