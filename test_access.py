import pyodbc

DBQ = 'V:\\FWD\\Underseal\\Data\\2023\\todo\\ready\\02022026_update\\D2304249032\\US-31 LL-40\\US-31 NB RP-128+36 to RP-129+29 LN 3.accdb'
DSN = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + DBQ

def test_connect(label):
    print(f"  {label}: connecting...", end=" ", flush=True)
    conn = pyodbc.connect(DSN)
    print("OK")
    conn.close()

print("=== Testing which project import breaks pyodbc.connect ===\n")

test_connect("baseline (no project imports)")

print("\n1) import db")
import db
test_connect("after import db")

print("\n2) from ll_query import ll_query")
from ll_query import ll_query
test_connect("after import ll_query")

print("\n3) from mde_entry import read_mde, getGPS, read_pavtype")
from mde_entry import read_mde, getGPS, read_pavtype
test_connect("after import mde_entry")

print("\n4) from calculate import calc")
from calculate import calc
test_connect("after import calc")

print("\n5) import report")
import report
test_connect("after import report")

print("\n6) from ll_query import get_ll_obj, find_ll_no_given_req_no")
from ll_query import get_ll_obj, find_ll_no_given_req_no
test_connect("after import ll_query extras")

print("\n7) import tkinter stuff")
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
test_connect("after import tkinter")

print("\n8) import remaining (pickle, os, sys, warnings, traceback, re, numpy)")
import pickle as pkl
import os, sys
import warnings
warnings.filterwarnings("ignore")
import traceback, re
import numpy as np
test_connect("after all imports")

print("\n=== ALL PASSED ===")
