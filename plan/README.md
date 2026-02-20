# New Underseal Improvement Plan

Comprehensive plan for improving the FWD Analysis and Visualization Tool codebase.
Created: 2026-02-19

## Current Status (as of Session 3, 2026-02-20)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0: ArcGIS Dashboard Fix | IN PROGRESS | Diagnostic script pushed, awaiting Dr. Shin's output |
| Phase 1: Security + Stability | NOT STARTED | Highest priority after dashboard fix |
| Phase 2: Code Quality | PARTIAL | Logging (3.4) done; rest not started |
| Phase 3: Architecture | PARTIAL | Logging (4.3) done; rest not started |
| Phase 4: Testing | PARTIAL | Subprocess validation (5.1) done; rest not started |
| Phase 5: DevOps | NOT STARTED | .gitignore is quick win |

## Plan Documents

| Document | Description |
|----------|-------------|
| [01-security.md](01-security.md) | Security fixes (credentials, SQL injection) — **URGENT** |
| [02-stability.md](02-stability.md) | Bug fixes and stability improvements |
| [03-code-quality.md](03-code-quality.md) | Code cleanup, deduplication, modernization |
| [04-architecture.md](04-architecture.md) | Structural improvements and configuration |
| [05-testing.md](05-testing.md) | Testing strategy and validation |
| [06-devops.md](06-devops.md) | Git hygiene, CI, deployment |
| [SESSION-LOG.md](SESSION-LOG.md) | Session-by-session work log |

## Priority Order

1. **P0 — ArcGIS Dashboard**: Grey requests missing from map. Diagnostic script created.
2. **P0 — Security** (01): Exposed credentials in public repo. Must fix immediately.
3. **P1 — Stability** (02): Bugs that can cause crashes or data corruption.
4. **P2 — Code Quality** (03): Cleanup that makes future work safer and faster.
5. **P3 — Architecture** (04): Structural improvements for maintainability.
6. **P4 — Testing** (05): Validation to prevent regressions.
7. **P5 — DevOps** (06): Git, CI, deployment improvements.

## Key Files Added

| File | Purpose |
|------|---------|
| `diagnose_dashboard.py` | Diagnostic script for ArcGIS dashboard issue |
| `sql/arcgis_dashboard.sql` | Dashboard queries + connection metadata |
| `log_config.py` | Centralized logging configuration |

## How We Work

Since the user's INDOT work PC cannot access LLMs:
1. Claude makes code changes and pushes to GitHub
2. User pulls on work PC, runs the scripts, pushes logs
3. Claude reviews logs and iterates

All changes go to the `claude-fix` branch (based on `old_main` commit `c4a4d28`).
