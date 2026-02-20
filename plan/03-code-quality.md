# P2: Code Quality & Cleanup

## Status: NOT STARTED

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

**Fix**:
- [ ] Remove all unused imports
- [ ] Reducing loaded modules also reduces the DLL conflict surface

**Files**: `calculate.py`, `report.py`, `writefiles.py`, `MR_cal.py`

---

### 3.2 Deduplicate Functions

**Problem**: Several functions are duplicated across files.

| Function | File 1 | File 2 | Notes |
|----------|--------|--------|-------|
| `putstats()` | `db.py:114` | `calculate.py:276` | Slightly different (db.py has audit fields) |
| `putdata()` | `calculate.py:239` | `db.py:54` (putcalc) | Old vs new version |
| `get_pathstring()` | `report.py:569` | `report_page4.py:111` | Identical |
| `elab_dir()` / `dir_str()` | `report.py:27` | `report_page4.py:35` | Identical logic |

**Fix**:
- [ ] Remove `putstats()` and `putdata()` from `calculate.py` (the `db.py` versions are used)
- [ ] Move `get_pathstring()` to a shared utility module and import from both report files
- [ ] Consolidate `elab_dir()` / `dir_str()` into one function in one place

**Files**: `calculate.py`, `db.py`, `report.py`, `report_page4.py`

---

### 3.3 Remove Dead/Commented-Out Code

**Problem**: Significant chunks of commented-out code throughout:
- `calculate.py` — commented-out test code at bottom (lines 549-554)
- `report_page4.py` — commented-out test code at bottom (lines 410-451)
- `mde_entry.py` — scattered commented-out debug prints
- `db.py` — many commented-out print statements
- `MR_cal.py` — 40+ lines of commented-out test code (lines 86-125)

**Fix**:
- [ ] Remove all commented-out test code (it's preserved in git history)
- [ ] Remove debug print statements that are commented out
- [ ] Keep only meaningful code comments

**Files**: Multiple

---

### 3.4 Consistent Error Handling Pattern

**Problem**: Error handling is inconsistent — some functions raise exceptions with messages, some use bare `except:`, some print errors, some write to log files.

**Fix**:
- [ ] Establish a consistent pattern: use Python `logging` module (already set up in batch script)
- [ ] Import and use `logger` from a shared module in all files
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
