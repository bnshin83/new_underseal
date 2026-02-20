# P2: Code Quality & Cleanup

## Status: MOSTLY DONE (3.1, 3.2, 3.3 done — Sessions 5+6; 3.4 partial)

---

### 3.1 Remove Unused Imports

**Problem**: Many files import modules that are never used, adding to load time and the DLL conflict surface area.

**Affected**:
- `calculate.py:1` — `from pdb import line_prefix` (unused)
- `calculate.py:2` — `from sys import stderr` (unused)
- `calculate.py:3` — `from webbrowser import get` (unused)
- `calculate.py:10` — `import xlrd` (unused in active code)
- `report.py:6` — `from pydoc import Doc` (unused)
- `report.py:7` — `from venv import create` (unused)
- `report.py:8` — `from webbrowser import get` (unused)
- `writefiles.py:1` — `from sys import stderr` (unused)
- `writefiles.py:2` — `from webbrowser import get` (unused)
- `MR_cal.py:4` — `import openpyxl` (only in commented-out test code)

**Fix**: DONE — Session 5
- [x] Removed `from pdb import line_prefix`, `from sys import stderr`, `from webbrowser import get` from `calculate.py`
- [x] Removed `from pydoc import Doc`, `from venv import create`, `from webbrowser import get` from `report.py`
- [x] Removed `from sys import stderr`, `from webbrowser import get` from `writefiles.py`

**Files**: `calculate.py`, `report.py`, `writefiles.py`

---

### 3.2 Deduplicate Functions (DONE)

**Problem**: Several functions were duplicated across files.

**Fix**: Session 6 (2026-02-20):
- [x] Removed dead `putdata()` and `putstats()` from `calculate.py` (not called anywhere; live versions in `db.py`)
- [x] Simplified `dir_str()` in `report_page4.py` to dict lookup
- [x] Could NOT consolidate `get_pathstring()` or `dir_str()`/`elab_dir()` between report.py and report_page4.py due to circular import (report.py imports report_page4). Kept separate but simplified.

**Files**: `calculate.py`, `report_page4.py`

---

### 3.3 Remove Dead/Commented-Out Code (DONE)

**Problem**: 195 commented-out print statements and dead test blocks across 13 files.

**Fix**: Session 6 (2026-02-20):
- [x] Removed all 195 `# print(...)` statements across 13 files
- [x] Removed dead test blocks at bottom of `calculate.py`, `report_page4.py`, `MR_cal.py`, `comments.py`
- [x] Removed unused `blockPrint()`/`enablePrint()` functions from `calculate.py`
- [x] Removed now-unused `import sys,os` from `calculate.py`
- [x] Kept meaningful formula reference comments (Excel formula documentation)

**Files**: `calculate.py`, `db.py`, `report.py`, `writefiles.py`, `comments.py`, `mde_entry.py`, `match_images.py`, `excel.py`, `roadanalyzer.py`, `upload_results_batch_f25only.py`, `split_mde.py`, `upload_ll_batch.py`, `MR_cal.py`, `report_page4.py`

---

### 3.4 Consistent Error Handling Pattern (PARTIAL — logging infrastructure done)

**Problem**: Error handling is inconsistent — some functions raise exceptions with messages, some use bare `except:`, some print errors, some write to log files.

**Status**: PARTIAL — `log_config.py` created and integrated into 11 files (Session 2, 2026-02-20). All modules now use `logger = get_logger('module_name')`. Remaining work is converting bare `except:` clauses (see 2.8) and replacing remaining `print()` calls.

**Remaining Fix**:
- [x] Establish a consistent pattern: use Python `logging` module
- [x] Import and use `logger` from a shared module in all files
- [ ] Replace `print()` calls with `logger.info()` / `logger.warning()` / `logger.error()`

**Files**: All Python files

---

### 3.5 Module-Level Global Variables

**Problem**: `report_page4.py` uses module-level globals (`rp_val`, `dmi_val`) modified via `assign_values()`. This makes the module non-reentrant.

**Fix**:
- [ ] Pass `rp_val` and `dmi_val` as parameters to functions that need them
- [ ] Remove the global variables and `assign_values()` function

**Files**: `report_page4.py`, `report.py`

---

### 3.6 Type Hints for Core Functions

**Problem**: No type hints anywhere. Makes it hard to understand function contracts.

**Fix** (low priority, incremental):
- [ ] Add type hints to the most-called functions first:
  - `read_pavtype(path: str, f25_path: str) -> Tuple[float, float]`
  - `read_mde(...) -> Tuple[dict, str, str, dict]`
  - `calc(...) -> Tuple[dict, dict, dict, list, list]`
  - `upload_single_result(...) -> None`

**Files**: `mde_entry.py`, `calculate.py`, `upload_results_batch_f25only.py`
