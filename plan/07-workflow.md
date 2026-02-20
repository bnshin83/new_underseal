# P1.5: Workflow Improvements

## Status: PARTIAL (7.1 and 7.2 done — Session 4)
**Priority**: HIGH — these are daily pain points that slow down batch processing.

---

### 7.1 Image Failure Should Not Kill the Entry

**Problem**: A missing image file (e.g., `FileNotFoundError` on a `.jpg`) causes the entire F25 entry to fail and rollback, even though all calculations, deflections, moduli, and misc data are valid. The image matching is the last step — everything else succeeded.

**Seen in**: run_log.txt 2026-02-20 08:35:00 — `FileNotFoundError` on a single Cam1 image caused full rollback of LL-9378 EB.

**Fix**: DONE — Session 4
- [x] Wrapped image matching/copying in try-except inside `read_mde()`
- [x] If image matching fails, logs a warning but continues with the upload
- [x] Sets `ll_obj['img_dmi_dict'] = {}` on image failure so `putimg()` is skipped gracefully
- [x] Reports which images failed in the warning log

**Files**: `mde_entry.py`

---

### 7.2 Handle Unique Constraint Gracefully (Re-run Support)

**Problem**: If a previous run partially uploaded data (e.g., `stda_longlist` row exists but deflections/calculations are incomplete), re-running hits `ORA-00001: unique constraint (STDA.UNIQUE_STDA_LONGLIST) violated` and the entry is silently skipped with "Repeat entry" warning. The user has no way to complete the partial upload without manually deleting rows in SQL Developer.

**Fix**: DONE — Session 4
- [x] When `unique constraint` is caught, checks if existing entry is complete (has rows in all 6 tables)
- [x] If incomplete: deletes partial data and re-uploads from scratch (auto-cleanup)
- [x] If complete: skips with "Already uploaded (complete)" info message
- [x] Added `--force` flag to force re-upload even if entry exists (delete + re-insert)

**Files**: `upload_results_batch_f25only.py`

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

### 7.5 Speed Up Image Copying

**Problem**: Image copying from the network drive (V:\) to the image server is the slowest part of the pipeline. A 10-file batch takes 5-15 minutes, and most of that time is spent on `shutil.copy()` in `match_images.py`.

**Fix options** (investigate which gives best speedup):
- [ ] **Parallel image copy**: Use `concurrent.futures.ThreadPoolExecutor` to copy multiple images simultaneously. Network I/O is the bottleneck, so threading helps.
- [ ] **Skip already-copied images**: Check if the destination file already exists (and has the same size) before copying. Avoids redundant work on re-runs.
- [ ] **Deferred image copy**: Upload calculations immediately, copy images in the background or as a separate step. User gets results faster.
- [ ] **Batch copy with robocopy**: On Windows, `robocopy` is much faster than Python `shutil.copy()` for network drives. Could shell out to robocopy for the entire image folder.

**Files**: `match_images.py`, `mde_entry.py`

---

### 7.6 Auto-Email Reports to Advisor

**Problem**: After every batch, user manually emails the generated .docx reports to their advisor. This is repetitive — same recipient, same format every time.

**Fix**:
- [ ] Add `--email` flag to `upload_results_batch_f25only.py`
- [ ] After all reports are generated, compose an Outlook email (via `win32com` or `smtplib`) with:
  - To: configurable recipient (default: advisor's email)
  - Subject: auto-generated from request IDs and routes
  - Body: summary of what was processed (LL numbers, routes, directions)
  - Attachments: all generated .docx report files
- [ ] Use `win32com.client` to create a draft in Outlook (user can review before sending) rather than auto-sending
- [ ] Alternative: just open the folder containing reports so user can drag-and-drop into email

**Files**: new `email_report.py`, `upload_results_batch_f25only.py`

---

## Full Workflow (Current vs Improved)

### Current Workflow
1. Manually create .txt file with F25 paths
2. Run Python script in terminal
3. Wait 5-15 min (image copying is slow)
4. If errors: manually check error log, create new .txt, re-run
5. If unique constraint: manually delete rows in SQL Developer, re-run
6. Check ArcGIS dashboard
7. Manually email reports to advisor

### Improved Workflow (after all 7.x items)
1. Point script at a folder → it finds all F25 files automatically (7.3)
2. Run Python script
3. Faster processing — parallel image copy (7.5)
4. Image failures don't lose calculations (7.1)
5. Partial uploads auto-cleanup on re-run (7.2)
6. Failed files → one-click retry (7.4)
7. Check ArcGIS dashboard
8. Reports auto-emailed as Outlook draft (7.6)

---

### Implementation Order

| Item | Priority | Reason |
|------|----------|--------|
| 7.1 Image failure isolation | CRITICAL | Prevents data loss — calculations are thrown away for no reason |
| 7.2 Unique constraint handling | CRITICAL | Enables clean re-runs without manual SQL cleanup |
| 7.5 Speed up image copying | HIGH | Biggest time bottleneck in the pipeline |
| 7.4 Auto-retry failed files | HIGH | Natural follow-up to 7.2 — makes re-runs one-click |
| 7.3 Auto-generate txt from folder | MEDIUM | Convenience — saves time but current workflow works |
| 7.6 Auto-email reports | MEDIUM | Saves a few minutes per batch, nice quality-of-life |
