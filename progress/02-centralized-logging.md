# 02 — Centralized Logging System

**Date**: 2026-02-19

## What Was Done

Added a centralized logging system so every script logs to a single `run_log.txt` in the repo root. Previously only `upload_results_batch_f25only.py` had logging; all other scripts used scattered `print()` statements with no persistent log file.

### Created

- `log_config.py` — shared logging module with `get_logger(name)` that writes to `run_log.txt` (append mode) + stdout

### Modified (11 files)

| File | Changes |
|------|---------|
| `upload_results_batch_f25only.py` | Replaced inline `logging.basicConfig` with `from log_config import get_logger`; converted 5 bare `print()` to logger calls |
| `upload_ll_batch.py` | Added logger + run start/end markers; converted 3 prints |
| `fill_gps.py` | Added logger + run markers; converted 4 prints; fixed bug where one `print()` was missing `file=f` |
| `find_f25_files.py` | Added logger; converted 2 prints |
| `correct_f25_format.py` | Added logger; converted 2 prints |
| `sync_ll_2022_6_28.py` | Added logger; converted 3 prints (improved `print(ll_no)` to include context) |
| `mde_entry.py` | Added logger; converted 1 print to `logger.warning` |
| `match_images.py` | Added logger; converted 2 prints |
| `ll_info_entry.py` | Added logger; converted 1 print to `logger.debug` |
| `ll_query.py` | Added logger; converted 2 prints (1 debug, 1 info) |
| `split_mde.py` | Added logger; converted 1 print |

### Not Modified

- All `print(..., file=f)` calls that write to per-run error log files were kept as-is (they serve a different purpose — user-facing error files in the data directory)
- Files with 0 active prints: `calculate.py`, `db.py`, `report.py`, `report_page4.py`, `writefiles.py`, `MR_cal.py`, `roadanalyzer.py`, `excel.py`, `comments.py`, `query_db.py`, `copy_imgs.py`

## Log Format

```
2026-02-19 14:30:01 [INFO] [upload_results_batch] ============================================================
2026-02-19 14:30:01 [INFO] [upload_results_batch] RUN STARTED: 2026-02-19 14:30:01
2026-02-19 14:30:01 [INFO] [upload_results_batch] txt_path: D:\FWD Data\input.txt
2026-02-19 14:30:02 [INFO] [mde_entry] Copying images ...
2026-02-19 14:30:03 [WARNING] [match_images] Cannot convert to float image_filename: bad.tif
2026-02-19 14:30:05 [ERROR] [upload_results_batch] EXCEPTION: Access subprocess failed...
```

## Workflow

1. **User runs any script on the INDOT work PC** — e.g. `upload_results_batch_f25only.py`, `upload_ll_batch.py`, `fill_gps.py`, etc.
2. **All output appends to `run_log.txt`** in the repo root. Every entry has timestamp, level, and module name.
3. **User pushes after running:**
   ```
   cd new_underseal
   git add run_log.txt
   git commit -m "run log from today"
   git push
   ```
4. **Claude reads the log** on the next session and can diagnose issues, see what succeeded/failed, and suggest fixes.
5. **If the log gets too large**, the user can delete `run_log.txt` and the next run creates a fresh one.
