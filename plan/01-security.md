# P0: Security Fixes

## Status: MOSTLY DONE (1.1 + 1.2 code changes done — Sessions 4-5)
**Priority**: Old passwords still in git history (need BFG or make repo private)

---

### 1.1 Rotate and Remove Hardcoded Credentials

**Problem**: `db.py` contains plaintext passwords committed to the public repo `bnshin83/new_underseal`:
- Line 10: `password = 'Purduehamp4147'` (dev_wen — local dev Oracle)
- Line 28: `password = 'emerald-olive-944'` (ecn_wen, ecn_shin — Purdue ECN Oracle)
- Line 46: `password = 'emerald-olive-944'` (ecn_shin)
- Line 49: `password = 'drwsspadts1031$'` (shin — INDOT production Oracle)

**Fix**:
- [ ] Contact INDOT R&D IT to rotate the production password (`shin` env)
- [ ] Contact Purdue ECN to rotate `SPR4450` password
- [x] Modify `db.py` to read credentials from environment variables (Session 4)
- [x] Also fixed `sharepoint_update.py` and `sharepoint_update copy.py` (Session 4)
- [x] Add a `.env.example` file showing required env vars (without actual values) (Session 4)
- [x] Add `.env` to `.gitignore` (Session 4)
- [ ] Use `git filter-branch` or BFG Repo Cleaner to purge credentials from git history
- [ ] Consider making the repo private if it should remain accessible only to INDOT/Purdue

**Files**: `db.py`

---

### 1.2 Fix SQL Injection via String Concatenation

**Problem**: Multiple files build SQL queries by concatenating user-controlled strings directly into SQL statements. While the risk is low (data comes from local files and Excel), a malformed filename or Excel cell containing a single quote will crash the query, and this is bad practice.

**Affected files and lines**:
- `ll_query.py:106-128` — `compose_ll_entry_string()` — 8+ fields interpolated
- `ll_info_entry.py:63-96` — `compose_ll_info_entry_string()` — 15+ fields interpolated
- `query_db.py:6,17,29-30,42-43,52-54` — All query functions use `.format()`
- `find_f25_files.py:20-22` — `req_no` concatenated into SQL

**Fix**:
- [x] Convert all string-concatenated SQL to parameterized queries using `:param` bind variables (Session 5)
- [x] `ll_query.py`: `compose_ll_entry_string()` replaced with inline bind params in `ll_query()`, `find_ll_no_given_req_no()` converted
- [x] `ll_info_entry.py`: `compose_ll_info_entry_string()` now returns dict only; `ll_info_entry()` uses bind params
- [x] `query_db.py`: All 5 functions converted to bind variables
- [x] `find_f25_files.py`: Converted to bind variables
- [x] `fill_gps.py`: `idstr` query converted to bind variables
- [x] `upload_ll_batch.py`: `delete_rows` converted to bind variables
- [ ] Test with filenames containing special characters (single quotes, semicolons)

**Files**: `ll_query.py`, `ll_info_entry.py`, `query_db.py`, `find_f25_files.py`

---

### 1.3 Oracle DSN Strings Exposure

**Problem**: `db.py` also contains Oracle hostnames and connection strings:
- `dotorad002vl.state.in.us:1621/INDOT3DEV` (INDOT production)
- `oracle.ecn.purdue.edu:1521/primary` (Purdue ECN)

**Fix**:
- [ ] Move DSN strings to environment variables or a config file
- [ ] This is lower priority than passwords but should be addressed alongside 1.1

**Files**: `db.py`
