import pyodbc
import cx_Oracle
import shutil
import subprocess
import sys

accdb_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
mde_path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.mde'
ACCESS_DSN = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + accdb_path

def test_pillow_version(version):
    """Install a specific Pillow version and test if pyodbc.connect works."""
    print("\n" + "="*60)
    print("Testing Pillow=={}".format(version))
    print("="*60)

    # Install
    print("  Installing Pillow=={}...".format(version))
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "Pillow=={}".format(version), "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print("  INSTALL FAILED: {}".format(result.stderr.strip()))
        return None
    print("  Installed OK")

    # We need a fresh process because PIL is already loaded in this one.
    # Run a subprocess to test.
    test_code = """
import pyodbc
import cx_Oracle
import shutil

cx_Oracle.init_oracle_client(lib_dir=r"C:\\Users\\bshin\\Documents\\instantclient-basic-windows.x64-21.3.0.0.0\\instantclient_21_3")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
cursor = ora_con.cursor()
cursor.execute("SELECT longlist_no FROM stda_longlist_info WHERE request_no='D2304249032'")
for r in cursor:
    pass
cursor.close()

shutil.copy(r'{mde}', r'{accdb}')

from PIL import Image
print("PIL version: " + Image.__version__)

conn = pyodbc.connect(r'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={accdb}')
print("ACCESS OK")
conn.close()
ora_con.close()
""".format(mde=mde_path, accdb=accdb_path)

    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True, text=True, timeout=30
    )

    if "ACCESS OK" in result.stdout:
        print("  RESULT: PASSED - Pillow=={} works!".format(version))
        return True
    else:
        print("  RESULT: FAILED - hangs or crashes")
        if result.stdout.strip():
            print("  stdout:", result.stdout.strip())
        if result.stderr.strip():
            print("  stderr:", result.stderr.strip()[:200])
        return False


# Versions to test (newest to oldest)
versions = ["9.4.0", "9.3.0", "9.2.0", "9.1.1", "9.0.0", "8.4.0"]

print("Current Pillow version test:")
from PIL import Image
print("  Currently installed: Pillow=={}".format(Image.__version__))

results = {}
for v in versions:
    try:
        results[v] = test_pillow_version(v)
    except subprocess.TimeoutExpired:
        print("  RESULT: FAILED - timed out (hung)")
        results[v] = False
    except Exception as e:
        print("  RESULT: ERROR - {}".format(e))
        results[v] = None

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
for v in versions:
    status = {True: "PASS", False: "FAIL", None: "SKIP"}[results.get(v)]
    print("  Pillow=={}: {}".format(v, status))

# Restore current version
working = [v for v in versions if results.get(v) == True]
if working:
    print("\nRecommended: pip install Pillow=={}".format(working[0]))
    # Install the newest working version
    newest_working = working[0]
    print("Installing Pillow=={}...".format(newest_working))
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow=={}".format(newest_working), "--quiet"])
    print("Done!")
else:
    print("\nNo working version found. Will apply code fix instead.")
