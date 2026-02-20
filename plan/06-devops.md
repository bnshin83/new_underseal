# P5: DevOps & Git Hygiene

## Status: PARTIAL (6.1 done — Session 4)

---

### 6.1 Add `.gitignore` (DONE — Session 4)

**Problem**: No `.gitignore` file. Binary files, temp files, and sensitive data can accidentally be committed:
- `c.DMP`, `EXPDAT.DMP` (Oracle dump files, already in repo)
- `*.accdb` (temp copies of MDE files)
- `*.pkl` (pickle files from `unused_var_dict/`)
- `fig.png` (generated chart)
- `run_log.txt` (intentionally committed for remote debugging, but may want to exclude later)
- `page_4.docx` (temp report file)
- `__pycache__/`, `*.pyc`
- `.env` (credentials)

**Fix**:
- [ ] Create `.gitignore`:
  ```
  # Python
  __pycache__/
  *.pyc
  *.pyo

  # Environment
  .env
  *.DMP

  # Generated files
  fig.png
  page_4.docx

  # Temp files
  *.accdb
  unused_var_dict/

  # IDE
  .vscode/
  .idea/

  # Keep run_log.txt for remote debugging (remove this line when no longer needed)
  # run_log.txt
  ```

**Files**: New `.gitignore`

---

### 6.2 Clean Up Binary Files from Git History

**Problem**:
- `YGJ.exe` (443KB Fortran executable) is in the repo
- `EXPDAT.DMP` (36KB Oracle dump) is in the repo
- `c.DMP` (0 bytes) is in the repo

**Fix**:
- [ ] Decide if `YGJ.exe` should remain in the repo (convenient for deployment) or be distributed separately
- [ ] If keeping: add a note in README about the Fortran dependency
- [ ] If removing: use BFG Repo Cleaner to purge from history, document where to obtain it

---

### 6.3 Branch Strategy

**Current branches**:
- `main` — has diverged commits, unclear state
- `old_main` — original code at commit `c4a4d28`
- `claude-fix` — our fixes based on `old_main`
- `shin_dev` — Dr. Shin's development branch
- `debug-prints` — debug investigation branch

**Fix**:
- [ ] Once `claude-fix` is validated, merge it into `main`
- [ ] Delete `debug-prints` branch (served its purpose)
- [ ] Keep `old_main` as a reference tag
- [ ] Establish convention: work on feature branches, merge to `main` when tested

---

### 6.4 README Update

**Problem**: Current `README.md` is just one line: "# new_underseal"

**Fix**:
- [ ] Add project description (FWD Analysis and Visualization Tool)
- [ ] Add setup instructions (Python 3.9, pipenv, Oracle client, Fortran)
- [ ] Add usage instructions (reference the SPR-4450 manual)
- [ ] Add environment variable documentation
- [ ] Keep it concise — the SPR-4450 manual has full details

---

### 6.5 Consider Making Repo Private

**Problem**: The repo is public on GitHub (`bnshin83/new_underseal`) but contains:
- Government infrastructure credentials (even after rotation, future credentials could leak)
- Internal INDOT network hostnames
- INDOT-specific business logic

**Fix**:
- [ ] Discuss with Dr. Shin whether the repo should be made private
- [ ] If public is required (e.g., for JTRP publication requirements), ensure all credentials are externalized first
