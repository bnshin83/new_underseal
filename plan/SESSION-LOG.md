# Session Log

## Session 1 — 2026-02-19

### Problem
`upload_results_batch_f25only.py` stopped working on user's INDOT work PC. Script would run and exit silently — no error messages, no traceback, no error log files.

### Investigation
1. Added DEBUG print statements (pushed via Git, user ran on work PC)
2. Narrowed crash to `read_pavtype()` → `pyodbc.connect()` to Access `.accdb`
3. Tested pyodbc + Access in isolation → works fine
4. Tested with cx_Oracle → works fine
5. Found: importing `mde_entry` module (~485 modules loaded) creates DLL conflict between Oracle Instant Client and Access ODBC driver
6. PIL/Pillow was initially suspected → removing it did NOT fix the issue

### Root Cause
DLL conflict between cx_Oracle (Oracle Instant Client) and Microsoft Access ODBC driver when many modules are loaded in the same process. Triggered by a recent system update.

### Fix Applied
- Subprocess isolation for all Access DB queries (clean PATH, no Oracle DLLs)
- `_get_clean_env()` strips Oracle Instant Client dirs from PATH
- `_access_connect()` reads all 6 Access tables via subprocess + pickle temp file
- `read_pavtype()` runs Access query in subprocess + JSON stdout
- Lazy PIL import in `match_images.py`
- Added `logging` to `upload_results_batch_f25only.py` (writes to `run_log.txt`)
- Created `DEBUG_LOG.md` documenting the investigation

### Branch
`claude-fix` based on `origin/old_main` (commit `c4a4d28`)

### Code Review
Performed full codebase review of all Python files. Identified:
- Hardcoded credentials in public repo (URGENT)
- SQL injection vulnerabilities
- Global variable bugs
- Destructive import side effects
- File handle leaks
- Duplicate functions
- Unused imports

### Artifacts Created
- `DEBUG_LOG.md` — investigation documentation
- `plan/` directory — comprehensive improvement plan (6 documents)
- Memory bank — `MEMORY.md`, `architecture.md`

### Next Steps
1. User tests `claude-fix` branch on work PC
2. Push `run_log.txt` for review
3. Credential rotation (P0 security)

---

## Session 2 — 2026-02-20

### Context
Dr. Shin pulled `claude-fix` branch and ran batch upload on INDOT work PC. Pushed `run_log.txt` and reported results.

### Work Done
1. **Centralized logging**: Created `log_config.py` with `get_logger(name)` function. Integrated into 11 Python files. All output goes to `run_log.txt` + stdout.
2. **Fixed `user_input_dict` NameError**: Added `user_input_dict = {}` initialization before loop in `upload_results_batch_f25only.py`.
3. **Fixed pandas/pyodbc import order crash**: Reordered imports in subprocess scripts — `pyodbc.connect()` must happen BEFORE `import pandas` to avoid numpy DLL conflict (0xC0000005).
4. **Created backup repo**: `bnshin83/Underseal_new_backup` (private) — full copy of Underseal_new folder from INDOT PC.
5. **Verified end-to-end run**: Both EB and WB directions processed successfully.

### Key Discovery
Import order matters in subprocess scripts: `pyodbc.connect()` must execute before `import pandas` (which loads numpy). The numpy DLLs interfere with the Access ODBC driver, causing a silent 0xC0000005 crash.

---

## Session 3 — 2026-02-20

### Context
ArcGIS Pro FWD dashboard not showing data for "grey requests" (high LL numbers like 9384+). All data exists in Oracle tables, but entire requests are missing from the dashboard map.

### Work Done
1. **Created `diagnose_dashboard.py`**: Comprehensive diagnostic script that Dr. Shin runs on work PC. Checks all 6 tables in the INNER JOIN chain, data types (via Oracle DUMP), NULL GPS coordinates, drop_no alignment, and runs the full dashboard query for specific LL numbers. Also supports comparing a broken LL against a known working one.
2. **Created `sql/arcgis_dashboard.sql`**: Saved the current ArcGIS dashboard queries with full documentation — the 3-layer architecture (FWD_Dashboard_numeric point layer, image_layer, route line layer), JOIN chain documentation, and diagnostic notes.
3. **Updated plan documents**: Marked completed items in 02-stability.md (2.3 done, 2.10 added), 03-code-quality.md (3.4 partial), 04-architecture.md (4.3 done), 05-testing.md (5.1 done). Updated README.md with current status table.

### Root Cause (RESOLVED)
The Oracle data and upload code were fine. The ArcGIS Dashboard had a **Category Selector** widget with a **Maximum categories** limit that excluded newer requests. The grey requests (LL 9384+) were beyond this limit and not displayed on the dashboard map, even though the data was present in Oracle and the web feature layer.

**Fix**: Increased the Maximum categories limit in the dashboard Category Selector widget.

### Next Steps
1. Continue to Phase 1 (security + stability fixes)

---

### Session 3 Status
- [x] `diagnose_dashboard.py` created and pushed
- [x] `sql/arcgis_dashboard.sql` created
- [x] Plan docs updated (02, 03, 04, 05, README)
- [x] Diagnostic run by Dr. Shin — Oracle data confirmed OK
- [x] Root cause found: ArcGIS Dashboard Category Selector max categories limit
- [x] Dashboard fixed by Dr. Shin — grey requests now visible

---

## Session 4 — 2026-02-20

### Work Done
1. **Created proper `.gitignore`**: Replaced corrupted UTF-16 gitignore. Added rules for `__pycache__/`, `.env`, `.vscode/`, `*.DMP`, `*.xlsx`, `*.csv`, `unused_var_dict/`, etc. Removed 4818 pkl files + other junk from git tracking.
2. **Externalized credentials (1.1)**: Removed 4 hardcoded passwords from `db.py`, 2 from `sharepoint_update.py`, 2 from `sharepoint_update copy.py`. Now reads from environment variables (`UNDERSEAL_SHIN_PASSWORD`, `UNDERSEAL_ECN_PASSWORD`, `UNDERSEAL_DEV_WEN_PASSWORD`, `UNDERSEAL_SHAREPOINT_PASSWORD`). Created `.env.example` template.
3. **Fixed global `id` variable bug (2.2)**: Renamed `global id` to local `longlist_id` in `upload_single_result()`, now returned as a value. Reset at top of each loop iteration. Eliminates stale rollback risk.
4. **Isolated image failure from entry upload (7.1)**: Wrapped image matching in try-except in `read_mde()`. If images fail, logs warning but calculations/deflections still upload to Oracle. Sets `img_dmi_dict = {}` so `putimg()` is skipped gracefully.
5. **Implemented unique constraint handling (7.2)**: On `ORA-00001`, checks if existing entry is complete (all tables have data). If partial, auto-cleans and retries. If complete, skips with clear message. Added `--force` flag for forced re-upload.
6. **Fixed orphaned cursor (2.4)**: Removed unused `cursor = con.cursor()` and `cursor.close()` from `read_mde()`.

### Setup Required by Dr. Shin
After pulling these changes:
```
setx UNDERSEAL_SHIN_PASSWORD "your_password_here"
```
Set this as a Windows environment variable (permanent via System Properties > Environment Variables, or per-session via `set`).

### Next Steps (Session 5)
- Phase 1B: SQL injection fix (`ll_query.py`, `ll_info_entry.py`, `query_db.py`)
- Phase 2A: Remove unused imports
- Phase 2B: Bare `except:` → `except Exception:`
- Password rotation with INDOT IT
- Consider `git filter-branch` or BFG to purge old passwords from git history

---

## Session 5 — 2026-02-20

### Work Done
1. **SQL injection fix (1.2)**: Converted ALL string-concatenated SQL across 7 files to Oracle `:param` bind variables:
   - `ll_query.py`: Refactored `compose_ll_entry_string()` — eliminated the function, moved bind params directly into `ll_query()`. Fixed `find_ll_no_given_req_no()`.
   - `ll_info_entry.py`: `compose_ll_info_entry_string()` now returns dict only. `ll_info_entry()` uses bind params for both INSERT and SELECT.
   - `query_db.py`: All 5 functions (`get_ll_from_db`, `read_db`, `read_db_from_ll_no_year`, `get_unique_ll_no_list`, `update_db`, `update_pavtype`) converted.
   - `find_f25_files.py`: Request number query converted.
   - `fill_gps.py`: F25 info query converted.
   - `upload_ll_batch.py`: `delete_rows` converted.
2. **Remove unused imports (3.1)**: Removed 8 unused imports from `calculate.py`, `report.py`, `writefiles.py` (pdb, sys.stderr, webbrowser, pydoc, venv).
3. **Fix bare except clauses (2.8)**: All 11 bare `except:` across 9 files converted to specific exception types (`ValueError`, `IndexError`, `TypeError`, `OSError`, `Exception`).

### Next Steps (Session 6)
- Remaining stability: destructive import in report_page4.py (2.5), file handle leaks (2.6, 2.7), temp .accdb cleanup (2.9)
- Code quality: dedup functions (3.2), remove dead code (3.3)
- Architecture: centralized config (3A), subprocess abstraction (3B)
