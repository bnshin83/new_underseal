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

## Session 2 — (next session)

### Start-of-Session Checklist
- [ ] Read `plan/SESSION-LOG.md` for context
- [ ] Check if `run_log.txt` has been pushed
- [ ] Review any new commits on `claude-fix` or `main`
- [ ] Check plan status in `plan/*.md` files

### End-of-Session Checklist
- [ ] Update `SESSION-LOG.md` with work done
- [ ] Update plan files with task status changes
- [ ] Update `MEMORY.md` if new patterns discovered
- [ ] Commit and push changes
- [ ] Note any pending items for next session
