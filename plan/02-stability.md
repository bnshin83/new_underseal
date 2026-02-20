# P1: Stability & Bug Fixes

## Status: PARTIALLY DONE (subprocess fix applied)

---

### 2.1 DLL Conflict Fix (DONE)

**Problem**: cx_Oracle + Access ODBC driver hangs when ~485 modules loaded.
**Fix**: Subprocess isolation with clean PATH. Applied in `claude-fix` branch.
**Status**: DONE — needs user testing on work PC.

**Files**: `mde_entry.py` (read_pavtype, _access_connect, _get_clean_env)

---

### 2.2 Global `id` Variable Bug (DONE)

**Problem**: `upload_results_batch_f25only.py:93-94` uses `global id` inside `upload_single_result()`. This:
1. Shadows Python's built-in `id()` function
2. The `except` block at line 353 references `id` for rollback — if `ll_query()` fails before setting `id`, it could use a stale value from a previous loop iteration
3. If the first file fails before `ll_query()`, `id` is `None` (correct), but on subsequent iterations if `id` was set by a previous successful run, the rollback would delete the WRONG entry

**Fix**: Renamed `global id` to local `longlist_id`, returned from `upload_single_result()`, reset at top of each loop iteration.
**Status**: DONE — Session 4 (2026-02-20)

**Files**: `upload_results_batch_f25only.py`

---

### 2.3 Undefined `user_input_dict` Variable (DONE)

**Problem**: In `upload_results_batch_f25only.py`, when `args.user_input` is False (the normal code path, line 214-227), `user_input_dict` is never defined. It's passed to `upload_single_result()` at line 328. Currently doesn't crash because `compose_ll_entry_string()` only accesses it in the `args.user_input` branch, but it's a latent `NameError`.

**Fix**: Added `user_input_dict = {}` initialization before the loop (line 200).
**Status**: DONE — Session 2 (2026-02-20)

**Files**: `upload_results_batch_f25only.py`

---

### 2.4 Orphaned Cursor in `read_mde()` (DONE)

**Problem**: `mde_entry.py:228` creates `cursor = con.cursor()` from the Oracle connection, but after the subprocess fix, no Oracle queries are executed in `read_mde()`. The cursor is created and closed (line 360) without use, wasting a database resource.

**Fix**: Removed both lines.
**Status**: DONE — Session 4 (2026-02-20)

**Files**: `mde_entry.py`

---

### 2.5 Destructive Import Side Effect in `report_page4.py`

**Problem**: Lines 15-16 execute at **import time**:
```python
if os.path.exists('./page_4.docx'):
    os.remove("page_4.docx")
```
This silently deletes `page_4.docx` from the current working directory every time the module is imported, even if it's being imported for testing or inspection.

**Fix**:
- [ ] Remove lines 15-16 entirely (the file is never used in production; `gen_report()` saves with a proper filename)
- [ ] Or move this logic into a function that's explicitly called

**Files**: `report_page4.py`

---

### 2.6 File Handle Leak in `getGPS()`

**Problem**: `mde_entry.py:15` opens `f25_path` with `open()` but only closes at line 73. If an exception occurs between these lines, the file handle leaks.

**Fix**:
- [ ] Refactor to use `with open(f25_path, "r") as f25file:` context manager

**Files**: `mde_entry.py`

---

### 2.7 File Handle Leak in `getUnits()`

**Problem**: Same pattern at `mde_entry.py:96-97`. File opened, closed at line 127, no context manager.

**Fix**:
- [ ] Refactor to `with open(f25_path, "r") as f25file:`

**Files**: `mde_entry.py`

---

### 2.8 Bare `except:` Clauses (DONE)

**Problem**: Multiple files used bare `except:` which catches SystemExit, KeyboardInterrupt, etc.

**Fix**: All 11 bare `except:` converted to specific exception types (Session 5):
- `mde_entry.py`: `ValueError`, `(ValueError, IndexError)`, `OSError`
- `comments.py`: `Exception`
- `fill_gps.py`: `Exception`
- `upload_ll_batch.py`: `Exception`
- `match_images.py`: `Exception`
- `report_page4.py`: `(IndexError, TypeError)` (2 locations)
- `roadanalyzer.py`: `(ValueError, TypeError)`
- `folder_analyzer.py`: `Exception`
**Status**: DONE — Session 5 (2026-02-20)

---

### 2.9 Temporary `.accdb` Files Not Cleaned Up

**Problem**: Both `read_pavtype()` (line 191) and `read_mde()` (line 227) call `shutil.copy(path, newpath)` creating `.accdb` copies but never delete them after use. Over time, the data folder accumulates duplicate files.

**Fix**:
- [ ] Add cleanup after subprocess completes: `os.remove(newpath)` in a `finally` block
- [ ] Or use `tempfile.NamedTemporaryFile` with `.accdb` suffix instead of copying to a predictable path

**Files**: `mde_entry.py`

---

### 2.10 Import Order: pyodbc Before pandas (DONE)

**Problem**: In the subprocess scripts spawned by `_access_connect()`, `import pandas` must come AFTER `pyodbc.connect()`. NumPy DLLs (loaded by pandas) conflict with the Access ODBC driver, causing a silent crash (exit code 0xC0000005 / ACCESS_VIOLATION).

**Fix**: Reordered imports in subprocess script strings so `pyodbc.connect()` happens first, then `import pandas`.
**Status**: DONE — Session 2 (2026-02-20). Verified via successful end-to-end batch run.
