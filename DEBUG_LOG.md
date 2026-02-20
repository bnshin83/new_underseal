# Debug Log: pyodbc Access Driver Hang (2026-02-19)

## Problem
`upload_results_batch_f25only.py` stopped working — script would run and exit silently without completing. No error messages, no traceback, no error log files created.

The user reported: "it worked well for a long time, but something upgraded, then problem."

## Root Cause
**DLL conflict between cx_Oracle (Oracle Instant Client) and Microsoft Access ODBC driver.**

When the Python process has many modules loaded (specifically modules pulled in by `mde_entry.py` imports), `pyodbc.connect()` to an Access `.accdb` file **hangs indefinitely** — no Python exception, no traceback, just a silent deadlock.

This was triggered by a recent update (likely a Windows Update, VS Code extension update, or ODBC driver update) that changed how DLLs interact in memory.

### Key findings from debugging:
1. `pyodbc.connect()` to Access works fine in isolation
2. `cx_Oracle.connect()` to Oracle works fine in isolation
3. Both work fine together in a simple script
4. The hang occurs when `mde_entry.py` is imported (which pulls in ~485 modules including pandas, numpy, pyodbc, cx_Oracle, ctypes, etc.)
5. The hang is NOT caused by any single import — it's the combination of all loaded modules + Oracle connection + Access connection in the same process
6. PIL/Pillow was initially suspected but removing it did not fix the issue
7. A subprocess with a clean environment (Oracle DLLs removed from PATH) does NOT hang

### Specific crash evidence:
- `returncode=3221226505` (0xC0000005 = ACCESS_VIOLATION) on corrupted `.mde` files
- Silent process death with no traceback on the original code
- The `except:` block in the batch loop never fires because it's a native crash, not a Python exception

## Fix Applied
**Run all Access database queries in a subprocess** to isolate them from the cx_Oracle DLL environment.

### Changes to `mde_entry.py`:

1. **`read_pavtype()`** — replaced direct `pyodbc.connect()` with a subprocess that:
   - Strips Oracle Instant Client from PATH
   - Runs a minimal Python script that connects to Access and queries `e1, e2` from Thickness table
   - Returns results via JSON through stdout

2. **New `_access_connect()` helper** — used by `read_mde()`:
   - Strips Oracle Instant Client from PATH
   - Runs a subprocess that reads ALL needed Access tables (Deflections, DEFLECTIONS_MEASURED_CALCULATED, MODULI_ESTIMATED, Geophone_Positions, PLATE_GEOPHONE, Thickness)
   - Returns data via pickle temp file
   - `read_mde()` then uses `tables['TableName']` instead of `pd.read_sql()`

3. **`match_images.py`** — moved `from PIL import Image` from module level to inside the function where it's used (lazy import)

### Benefits of subprocess approach:
- Completely isolates Access ODBC driver from cx_Oracle DLLs
- Corrupted `.mde` files crash the subprocess, not the main process — batch continues processing other files
- Error messages include returncode, stdout, stderr, and file path for debugging

## Environment
- Python 3.9.12 (64-bit)
- pyodbc 4.0.35
- cx_Oracle with Oracle Instant Client 21.3
- Pillow 9.4.0
- pandas 1.5.3
- numpy 1.21.6
- Windows (INDOT workstation)
- Microsoft Access Driver (*.mdb, *.accdb)

## Branch Reference
- `original_main` — user's original code at commit `3f3a77e` (before any fixes)
- `main` (origin) — contains the subprocess fix
- `debug-prints` — contains debug print statements used during investigation
- `shin_dev` — user's development branch (untouched)

## Debug Process Summary
1. Added DEBUG 1-6 prints → crash happens inside `upload_single_result`
2. Added DEBUG A-O prints → crash at `read_pavtype()` specifically at `pyodbc.connect()`
3. Tested pyodbc + Access in isolation → works fine
4. Tested pyodbc + cx_Oracle + Access → works fine
5. Tested with project imports one by one → `mde_entry` import causes the hang
6. PIL/Pillow suspected → removing PIL did NOT fix it
7. Found that ~485 modules loaded by `mde_entry` create the DLL conflict
8. Subprocess with clean PATH → works
9. Applied subprocess fix to `read_pavtype()` and `read_mde()`

## Notes
- The `returncode=3221226505` (ACCESS_VIOLATION) on certain `.mde` files is a **separate issue** — those files are corrupted and would crash even the old code (the old code just died silently)
- If this fix causes performance issues (subprocess startup overhead), consider caching the subprocess or using `multiprocessing` instead
