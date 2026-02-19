import sys
print("Python:", sys.version)

print("TEST A: bare pyodbc connect (no pandas)...")
import pyodbc
conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=V:\\FWD\\Underseal\\Data\\2023\\todo\\ready\\02022026_update\\D2304249032\\US-31 LL-40\\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb')
print("TEST A: connected OK")
cursor = conn.cursor()
cursor.execute('select e1, e2 from Thickness')
row = cursor.fetchone()
print("TEST A: e1=", row[0], "e2=", row[1])
conn.close()
print("TEST A: done")

print("\nTEST B: now import pandas...")
import pandas as pd
print("TEST B: pandas imported, version:", pd.__version__)

print("TEST C: connect again after pandas import...")
conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=V:\\FWD\\Underseal\\Data\\2023\\todo\\ready\\02022026_update\\D2304249032\\US-31 LL-40\\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb')
print("TEST C: connected OK")
conn.close()
print("TEST C: done")

print("\nTEST D: import numpy then connect...")
import numpy as np
print("TEST D: numpy imported, version:", np.__version__)
conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=V:\\FWD\\Underseal\\Data\\2023\\todo\\ready\\02022026_update\\D2304249032\\US-31 LL-40\\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb')
print("TEST D: connected OK")
conn.close()
print("TEST D: done")

print("\nTEST E: import tkinter then connect...")
import tkinter as tk
print("TEST E: tkinter imported")
conn = pyodbc.connect('Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=V:\\FWD\\Underseal\\Data\\2023\\todo\\ready\\02022026_update\\D2304249032\\US-31 LL-40\\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb')
print("TEST E: connected OK")
conn.close()
print("TEST E: done")

print("\n=== ALL TESTS PASSED ===")
