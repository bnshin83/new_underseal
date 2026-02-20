# P1.5: Workflow Improvements

## Status: NOT STARTED
**Priority**: HIGH — these are daily pain points that slow down batch processing.

---

### 7.1 Image Failure Should Not Kill the Entry

**Problem**: A missing image file (e.g., `FileNotFoundError` on a `.jpg`) causes the entire F25 entry to fail and rollback, even though all calculations, deflections, moduli, and misc data are valid. The image matching is the last step — everything else succeeded.

**Seen in**: run_log.txt 2026-02-20 08:35:00 — `FileNotFoundError` on a single Cam1 image caused full rollback of LL-9378 EB.

**Fix**:
- [ ] Wrap image matching/copying in a try-except inside `read_mde()` or `upload_single_result()`
- [ ] If image matching fails, log a warning but continue with the upload (calculations, deflections, etc. still get committed)
- [ ] Set `ll_obj['img_dmi_dict'] = {}` on image failure so `putimg()` is skipped gracefully
- [ ] Report which images failed in the warning log so they can be fixed later

**Files**: `upload_results_batch_f25only.py`, `mde_entry.py`, `match_images.py`

---

### 7.2 Handle Unique Constraint Gracefully (Re-run Support)

**Problem**: If a previous run partially uploaded data (e.g., `stda_longlist` row exists but deflections/calculations are incomplete), re-running hits `ORA-00001: unique constraint (STDA.UNIQUE_STDA_LONGLIST) violated` and the entry is silently skipped with "Repeat entry" warning. The user has no way to complete the partial upload without manually deleting rows in SQL Developer.

**Fix**:
- [ ] When `unique constraint` is caught, check if the existing entry is complete (has rows in all 6 tables)
- [ ] If incomplete: delete the partial data and re-upload from scratch (auto-cleanup)
- [ ] If complete: skip with "Already uploaded" info message (current behavior, but with clearer message)
- [ ] Add `--force` flag to force re-upload even if entry exists (delete + re-insert)

**Files**: `upload_results_batch_f25only.py`, `ll_query.py`

---

### 7.3 Auto-Generate txt File from Folder Structure

**Problem**: User must manually create a .txt file listing F25 paths for every batch. This is tedious and error-prone, especially for large batches with many F25 files across subfolders.

**Fix**:
- [ ] Add `--folder` flag to `upload_results_batch_f25only.py` that accepts a root folder path
- [ ] Script recursively finds all `.F25` files under that folder
- [ ] Groups them by request number (from folder structure)
- [ ] Generates the txt file automatically, or processes directly without a txt file
- [ ] Keep `--txt_path` and `--gui` as alternatives for backward compatibility

**Files**: `upload_results_batch_f25only.py`

---

### 7.4 Auto-Retry Failed Files

**Problem**: If 3 out of 10 files fail in a batch, the user has to manually figure out which ones failed (from the error log), create a new txt file with just those paths, and re-run. This is slow and error-prone.

**Fix**:
- [ ] At the end of a batch run, write a `*_retry.txt` file containing only the failed F25 paths
- [ ] Log a clear message: "3 files failed. Re-run with: python upload_results_batch_f25only.py --txt_path <retry_file>"
- [ ] Add `--retry` flag that automatically picks up the retry file from the previous run
- [ ] Combine with 7.2 (unique constraint handling) so retries work cleanly

**Files**: `upload_results_batch_f25only.py`

---

### Implementation Order

| Item | Priority | Reason |
|------|----------|--------|
| 7.1 Image failure isolation | CRITICAL | Prevents data loss — calculations are thrown away for no reason |
| 7.2 Unique constraint handling | CRITICAL | Enables clean re-runs without manual SQL cleanup |
| 7.4 Auto-retry failed files | HIGH | Natural follow-up to 7.2 — makes re-runs one-click |
| 7.3 Auto-generate txt from folder | MEDIUM | Convenience — saves time but current workflow works |
