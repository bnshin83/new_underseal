# New Underseal Improvement Plan

Comprehensive plan for improving the FWD Analysis and Visualization Tool codebase.
Created: 2026-02-19

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

1. **P0 — Security** (01): Exposed credentials in public repo. Must fix immediately.
2. **P1 — Stability** (02): Bugs that can cause crashes or data corruption.
3. **P2 — Code Quality** (03): Cleanup that makes future work safer and faster.
4. **P3 — Architecture** (04): Structural improvements for maintainability.
5. **P4 — Testing** (05): Validation to prevent regressions.
6. **P5 — DevOps** (06): Git, CI, deployment improvements.

## How We Work

Since the user's INDOT work PC cannot access LLMs:
1. Claude makes code changes and pushes to GitHub
2. User pulls on work PC, runs the scripts, pushes logs
3. Claude reviews logs and iterates

All changes go to the `claude-fix` branch (based on `old_main` commit `c4a4d28`).
