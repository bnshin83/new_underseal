# P3: Architecture & Configuration

## Status: NOT STARTED

---

### 4.1 Configuration File

**Problem**: Hardcoded paths are scattered throughout the codebase:
- Oracle Instant Client paths in `db.py` and `mde_entry.py`
- Fortran executable path `C:/Aashto/YGJ.exe` in `calculate.py:448`
- Fortran data files `C:/Aashto/*.dat` in `writefiles.py` and `calculate.py`
- Image server root `\\dotwebp016vw/data/FWD/` in argparse default
- Image URL prefix `https://resapps.indot.in.gov/photoviewer/data/FWD/` in `db.py:218`

Each developer (shin, wen) has different paths, managed by `dev_env` arg for DB but not for anything else.

**Fix**:
- [ ] Create `config.py` or `config.ini` that centralizes all paths:
  ```python
  # config.py
  import os

  ORACLE_CLIENT_DIR = os.environ.get('ORACLE_CLIENT_DIR',
      r"C:\Users\bshin\Documents\instantclient-basic-windows.x64-21.3.0.0.0\instantclient_21_3")
  FORTRAN_EXE = os.environ.get('FORTRAN_EXE', r"C:\Aashto\YGJ.exe")
  FORTRAN_DIR = os.environ.get('FORTRAN_DIR', r"C:\Aashto")
  IMAGE_SERVER_ROOT = os.environ.get('IMAGE_SERVER_ROOT', r"\\dotwebp016vw\data\FWD")
  IMAGE_URL_PREFIX = os.environ.get('IMAGE_URL_PREFIX',
      "https://resapps.indot.in.gov/photoviewer/data/FWD/")
  ```
- [ ] Update all files to import from `config.py`
- [ ] Env vars override defaults (allows different configs per machine without code changes)

**Files**: New `config.py`, modify `db.py`, `mde_entry.py`, `calculate.py`, `writefiles.py`, `db.py`

---

### 4.2 Project Structure Reorganization

**Problem**: All 20+ Python files are in a flat directory. SQL files, documentation, executables, dump files all mixed together.

**Current structure**: Flat — everything in root directory.

**Proposed structure** (minimal disruption):
```
new_underseal/
├── config.py                    # NEW: centralized configuration
├── db.py                        # Oracle connection + upload functions
├── mde_entry.py                 # Access DB reads + F25 parsing
├── calculate.py                 # FWD calculations
├── report.py                    # Report generation
├── report_page4.py              # Report page 4 details
├── ll_query.py                  # LongList query functions
├── ll_info_entry.py             # LongList info entry
├── upload_results_batch_f25only.py  # Main batch entry point
├── upload_ll_batch.py           # LongList upload entry point
├── match_images.py              # Image matching
├── comments.py                  # F25 comment extraction
├── excel.py                     # Excel utility functions
├── query_db.py                  # DB query utilities
├── MR_cal.py                    # MR/SN calculation
├── writefiles.py                # Write Fortran input files
├── roadanalyzer.py              # ESAL calculations
├── tools/                       # NEW: standalone utility scripts
│   ├── fill_gps.py
│   ├── find_f25_files.py
│   ├── correct_f25_format.py
│   ├── split_mde.py
│   ├── copy_imgs.py
│   └── sync_ll_2022_6_28.py
├── sql/                         # NEW: SQL files
│   ├── connection1.sql
│   ├── GIS_query.sql
│   ├── query_for_arcGIS.sql
│   ├── QueryForArcGIS_DrShin_11_9_2022.sql
│   ├── queryForArcGIS_DrShin.sql
│   ├── queryForGIS.sql
│   ├── QueryForKaren.sql
│   ├── QueryGIS_2_12_2022.sql
│   ├── check_size.sql
│   ├── sql_delete_rows.sql
│   └── reset_with_images.sql
├── plan/                        # Improvement plan docs
├── Pipfile
├── Pipfile.lock
├── .gitignore                   # NEW
├── .env.example                 # NEW: template for credentials
├── README.md
└── DEBUG_LOG.md
```

**Note**: This is optional and low priority. The flat structure works fine for a small team. Only pursue if the user wants it.

**Files**: Directory restructuring + import path updates

---

### 4.3 Logging Infrastructure

**Problem**: Logging was added to `upload_results_batch_f25only.py` (our fix) but other scripts (`upload_ll_batch.py`, `fill_gps.py`, etc.) still use `print()` and manual error log files.

**Fix**:
- [ ] Create a shared logging setup function:
  ```python
  # In config.py or a new logging_config.py
  def setup_logging(script_name):
      log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run_log.txt')
      logging.basicConfig(
          level=logging.INFO,
          format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
          handlers=[
              logging.FileHandler(log_path, mode='a', encoding='utf-8'),
              logging.StreamHandler(sys.stdout)
          ]
      )
      return logging.getLogger(script_name)
  ```
- [ ] Apply to `upload_ll_batch.py`, `fill_gps.py`, `find_f25_files.py`
- [ ] Keep the existing `_error_log.txt` files as a secondary output for user convenience

**Files**: `upload_ll_batch.py`, `fill_gps.py`, `find_f25_files.py`

---

### 4.4 Abstract Subprocess Access Pattern

**Problem**: The subprocess Access DB pattern (`_get_clean_env()` + subprocess script string) is duplicated between `read_pavtype()` and `_access_connect()`. If more Access queries are needed in the future, more duplication would occur.

**Fix** (optional, low priority):
- [ ] Create a generic `run_access_query(dbq_path, script_body)` helper
- [ ] Both `read_pavtype()` and `_access_connect()` call this helper
- [ ] Handles PATH cleaning, subprocess execution, error formatting in one place

**Files**: `mde_entry.py`
