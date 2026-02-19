import pyodbc
import pandas as pd

path = r'V:\FWD\Underseal\Data\2023\todo\ready\02022026_update\D2304249032\US-31 LL-40\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'

print("Step 1: connecting...")
conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + path)
print("Step 2: connected OK")

df = pd.read_sql('select * from Thickness ORDER BY SectionID ASC', conn)
print("Step 3: query OK")
print("e1=", df['e1'][0], "e2=", df['e2'][0])

conn.close()
print("Step 4: done")
