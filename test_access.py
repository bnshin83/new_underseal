import pyodbc
import cx_Oracle

DBQ = 'V:\\FWD\\Underseal\\Data\\2023\\todo\\ready\\02022026_update\\D2304249032\\US-31 LL-40\\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
ACCESS_DSN = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + DBQ

print("=== Testing Oracle + Access interaction ===\n")

# Test 1: Access before Oracle
print("TEST 1: Access connect BEFORE Oracle init...")
conn = pyodbc.connect(ACCESS_DSN)
print("TEST 1: Access connected OK")
conn.close()
print("TEST 1: closed OK")

# Test 2: Init Oracle client
print("\nTEST 2: cx_Oracle.init_oracle_client...")
cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
print("TEST 2: Oracle client initialized OK")

# Test 3: Access after Oracle init (but before Oracle connect)
print("\nTEST 3: Access connect AFTER Oracle init...")
conn = pyodbc.connect(ACCESS_DSN)
print("TEST 3: Access connected OK")
conn.close()
print("TEST 3: closed OK")

# Test 4: Oracle connect
print("\nTEST 4: Oracle connect...")
ora_con = cx_Oracle.connect(user='stda', password='drwsspadts1031$', dsn="dotorad002vl.state.in.us:1621/INDOT3DEV")
print("TEST 4: Oracle connected OK")

# Test 5: Access after Oracle connect (this is what the script does)
print("\nTEST 5: Access connect AFTER Oracle connect (the real scenario)...")
conn = pyodbc.connect(ACCESS_DSN)
print("TEST 5: Access connected OK")
conn.close()
print("TEST 5: closed OK")

ora_con.close()
print("\n=== ALL PASSED ===")
