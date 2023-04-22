import pyodbc
import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir=r"D:\shrey\Documents\INDOT_Project\instantclient-basic-nt-19.13.0.0.0dbru\instantclient_19_13")
msa_drivers = [x for x in pyodbc.drivers() ]
print(f'MS-Access drivers: \n{msa_drivers}')

conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=.\rename_test.accdb')
# D:\shrey\Documents\INDOT Project\Underseal_new\test3.accdb
# D:\shrey\Documents\INDOT Project\Underseal_new\test.accdb;
cursor = conn.cursor()
cursor.execute('select * from Deflections')
   
for row in cursor.fetchall():
    print (row)

con = cx_Oracle.connect(user='c##shrey', password = 'password', dsn="localhost/orcl.local")

