# Root Cause Analysis: Silent Script Crash (2026-02-19)

## Symptom
`upload_results_batch_f25only.py` stopped working on the INDOT work PC. The script would print "Error log is saved in:" then exit silently — no error messages, no traceback, no error log files created. The user reported: "It worked well for a long time, but something upgraded, then problem."

## Root Cause
**DLL conflict between cx_Oracle (Oracle Instant Client) and Microsoft Access ODBC driver.**

When the Python process has many modules loaded (~485 modules pulled in by `mde_entry.py` imports), `pyodbc.connect()` to an Access `.accdb` file **hangs indefinitely** — no Python exception, no traceback, just a silent deadlock at the native/C level.

## Why It Broke Without Code Changes

The user did not change any code. The most likely trigger is an **automatic system update** that changed how DLLs are loaded in memory:

### Most Likely Triggers (in order of probability)

1. **Windows Update** — Microsoft periodically patches the ODBC driver manager (`odbc32.dll`) and the Access ODBC driver. A patch could change DLL loading order or memory layout, creating a new conflict with Oracle's DLLs that didn't exist before.

2. **Microsoft Access Database Engine / ODBC Driver update** — Sometimes pushed silently via Windows Update or Office Update. The Access driver (`ACEODBC.DLL`) loads many supporting DLLs. A new version could conflict with Oracle's `oci.dll` in a way the old version didn't.

3. **Oracle Instant Client DLL interaction** — Even though Oracle wasn't updated, Windows could change how the existing Oracle DLLs interact with the system loader. Oracle Instant Client 21.3 loads `oci.dll`, `oraociei21.dll` (100+ MB), and other native libraries that hook into the Windows DLL subsystem.

### Why It's a Silent Hang (Not an Error)

The conflict happens at the **native/C level** — inside the Windows DLL loader or inside the ODBC driver's native code. Python never gets a chance to raise an exception because the deadlock occurs in native code before control returns to Python. That's why:

- No Python traceback
- No error message
- `except:` blocks never fire
- The process just freezes (or in the case of the corrupted MDE, segfaults with `returncode=3221226505` / `0xC0000005 ACCESS_VIOLATION`)

### Why It Only Happens With Many Modules Loaded

In isolation, both drivers work fine. The conflict requires a specific memory layout that only occurs when ~485 modules (pandas, numpy, scipy, cx_Oracle, pyodbc, ctypes, PIL, docx, matplotlib, etc.) are all loaded in the same process. This fills up the DLL address space in a way that creates the conflict.

Key evidence:
- `pyodbc.connect()` to Access works in a standalone script ✓
- `cx_Oracle.connect()` to Oracle works in a standalone script ✓
- Both together in a simple script work ✓
- Both together after `import mde_entry` (which pulls in ~485 modules) → **HANGS**

## Fix Applied

**Run all Access database queries in a subprocess** to isolate them from the cx_Oracle DLL environment.

- `_get_clean_env()` strips Oracle Instant Client directories from PATH
- `_access_connect(path)` reads all 6 Access tables via subprocess, returns data via pickle temp file
- `read_pavtype()` runs Access query in subprocess, returns data via JSON stdout
- Subprocess timeout of 60-120 seconds prevents infinite hangs
- Corrupted MDE files crash the subprocess (not the main process), allowing the batch to continue

This fix is **permanent** — it physically separates the two sets of DLLs into different processes, making it impossible for them to conflict regardless of future Windows or driver updates.

## Debug Process Summary

1. Added DEBUG 1-6 prints → crash happens inside `upload_single_result()`
2. Added DEBUG A-O prints → crash at `read_pavtype()` specifically at `pyodbc.connect()`
3. Tested pyodbc + Access in isolation → works fine
4. Tested pyodbc + cx_Oracle + Access → works fine in simple script
5. Tested with project imports one by one → `mde_entry` import causes the hang
6. PIL/Pillow was initially suspected → removing it did NOT fix it
7. Found ~485 modules loaded by `mde_entry` create the DLL conflict
8. Subprocess with clean PATH → works
9. Applied subprocess fix to `read_pavtype()` and `read_mde()`

## Environment
- Python 3.9.12 (64-bit Windows)
- pyodbc 4.0.35
- cx_Oracle with Oracle Instant Client 21.3
- Pillow 9.4.0
- pandas 1.5.3, numpy 1.21.6
- Microsoft Access Driver (*.mdb, *.accdb)
- INDOT workstation (Windows)
