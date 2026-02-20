# New Underseal Improvement Plan

Comprehensive plan for improving the FWD Analysis and Visualization Tool codebase.
Created: 2026-02-19

## Current Status (as of Session 6, 2026-02-20)

| Phase | Status | Notes |
|-------|--------|-------|
| Phase 0: ArcGIS Dashboard Fix | DONE | Root cause: Category Selector max categories limit in dashboard |
| Phase 1: Security + Stability | DONE | Credentials (1.1), SQL injection (1.2), global id (2.2), orphaned cursor (2.4), bare excepts (2.8), destructive import (2.5), file leaks (2.6/2.7), temp cleanup (2.9) all done |
| Phase 1.5: Workflow | DONE | Image failure isolation (7.1), re-run support (7.2), .gitignore (5A) all done |
| Phase 2: Code Quality | MOSTLY DONE | Unused imports (3.1), dedup (3.2), dead code (3.3), logging (3.4 partial) done |
| Phase 3: Architecture | PARTIAL | Logging (4.3) done; centralized config (3A), subprocess abstraction (3B) not started |
| Phase 4: Testing | PARTIAL | Subprocess validation (5.1) done; rest not started |
| Phase 5: DevOps | PARTIAL | .gitignore (5A) done; rest not started |

## Plan Documents

| Document | Description |
|----------|-------------|
| [01-security.md](01-security.md) | Security fixes (credentials, SQL injection) — **URGENT** |
| [02-stability.md](02-stability.md) | Bug fixes and stability improvements |
| [07-workflow.md](07-workflow.md) | Workflow improvements — image isolation, re-run, auto-retry |
| [03-code-quality.md](03-code-quality.md) | Code cleanup, deduplication, modernization |
| [04-architecture.md](04-architecture.md) | Structural improvements and configuration |
| [05-testing.md](05-testing.md) | Testing strategy and validation |
| [06-devops.md](06-devops.md) | Git hygiene, CI, deployment |
| [SESSION-LOG.md](SESSION-LOG.md) | Session-by-session work log |

## Priority Order

1. ~~**P0 — ArcGIS Dashboard**: DONE~~
2. **P0 — Security** (01): Exposed credentials in public repo. Must fix immediately.
3. **P1 — Stability** (02): Bugs that can cause crashes or data corruption.
4. **P1.5 — Workflow** (07): Image failure isolation, re-run support, auto-retry. Daily pain points.
5. **P2 — Code Quality** (03): Cleanup that makes future work safer and faster.
6. **P3 — Architecture** (04): Structural improvements for maintainability.
7. **P4 — Testing** (05): Validation to prevent regressions.
8. **P5 — DevOps** (06): Git, CI, deployment improvements.

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
