# P4: Testing Strategy

## Status: NOT STARTED

---

### 5.1 Validate Subprocess Fix on Work PC (DONE)

**Priority**: HIGH

**Status**: DONE — Session 2 (2026-02-20). Dr. Shin ran batch upload on work PC. Successful end-to-end run (EB + WB) confirmed. Key findings:
- Subprocess isolation works correctly
- Import order fix (pyodbc before pandas) prevents 0xC0000005 crash
- Logging captures all activity in `run_log.txt`
- Corrupted files fail gracefully without crashing main process

**Steps** (completed):
1. User pulled `claude-fix` branch on work PC
2. Ran the batch upload script with known-good F25 files
3. Pushed `run_log.txt` for review
4. Verified all items above

---

### 5.2 Unit Tests for Pure Calculation Functions

**Problem**: No automated tests exist. The codebase has testable pure functions that could be validated.

**Candidates for unit testing** (no DB or file system needed):
- `MR_cal.py` — `cal_mr_sn` class (MR/SN calculations)
- `calculate.py` — `temp_correction()`, `insitu_cbr()`, `aashto_esals()`, `indot_esals()`, `limit_esals()`, `insitu_mr()`, `get_log()`, `getSurfaceDefCrit()`, `getstats()`
- `roadanalyzer.py` — `set_vars()`, `calc_esal()`
- `comments.py` — `convert_chainage()`, `get_comments()` (needs sample F25 data)
- `match_images.py` — `ImageChainToChain()` (binary search, easy to test)
- `ll_query.py` — `check_f25_filename()` (regex validation)

**Fix**:
- [ ] Create `tests/` directory
- [ ] Start with `test_calculations.py`:
  ```python
  def test_temp_correction():
      # Known values from the Excel spreadsheet
      assert abs(temp_correction(70, 8) - expected) < 0.001

  def test_insitu_cbr():
      mr = np.array([5.0, 10.0, 15.0])
      result = insitu_cbr(mr)
      assert np.all(result <= 7)  # capped at 7

  def test_limit_esals():
      result = limit_esals(np.array([50000000]))
      assert result[0] == 40000000  # capped at 40M
  ```
- [ ] Add `test_mr_cal.py` comparing against known hand-calculation results
- [ ] Add `test_f25_parsing.py` with sample F25 snippets

**Files**: New `tests/` directory

---

### 5.3 Integration Test Script

**Problem**: The only way to test is to run the full batch pipeline against the production Oracle DB.

**Fix** (aspirational — depends on available infrastructure):
- [ ] Create a test script that:
  1. Connects to a dev/test Oracle instance (not production)
  2. Processes a small set of known-good F25/MDE files
  3. Verifies the uploaded data matches expected values
  4. Cleans up (deletes test rows)
- [ ] Requires a test Oracle instance or mock

**Alternative (simpler)**:
- [ ] Create a "dry run" mode that skips `db.putmde()`, `db.putcalc()`, `db.putstats()`, `db.putimg()` but still runs all calculations and generates reports
- [ ] Add `--dry_run` flag to `upload_results_batch_f25only.py`

---

### 5.4 Sample Data for Testing

**Problem**: No sample F25/MDE files in the repo for testing.

**Fix**:
- [ ] Add a `test_data/` directory with:
  - One small F25 file (anonymized if needed)
  - One corresponding MDE file
  - Expected output values for key calculations
- [ ] This enables anyone to validate the pipeline without access to INDOT data

**Note**: Check with Dr. Shin if sample FWD data can be included in the repo.
