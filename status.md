# AI Domain Trader — Status & Progress

Last updated: 2026-10-09
Repository: https://github.com/digiservbiz/ai-domain-trader
Roadmap: ROADMAP.md

## Current snapshot

| Measure | Current status | Notes |
|---|---:|---|
| Roadmap and project tracking | 100% | ROADMAP.md and this status file committed |
| Repository audit | ~85% | Preliminary source review; runtime/security validation remains open |
| Existing foundation usefulness | ~47% | Rough engineering estimate, not a test result |
| Autonomous investment intelligence | ~28% | Policy engine and isolated paper ledger exist; evidence, orchestration, and learning remain incomplete |
| Production readiness | ~29% | Tenant isolation implemented; CI currently blocked by one lint error |
| Overall target-product completion | ~22% | Current code is not yet verified end-to-end |

**Current phase:** Phase 1 — Safety foundation; Phase 0 audit remains open  
**Trading mode:** Paper trading only  
**Initial planning capital:** €1,000 EUR  
**Paper limits:** €100 maximum all-in per domain; €500 maximum deployed exposure; €500 reserve  
**Real purchases, bids, paid listings, and outbound email:** Not authorized. Live bidding fails closed unless both `TRADING_MODE=live` and `LIVE_TRADING_ENABLED=true` are configured; the default remains paper mode.

Percentages are engineering estimates, not test results. A commit is not considered verified until CI or a documented local check passes.

## Current blockers and known risks

- CI run 62 reached lint successfully through dependency installation but failed on one Ruff error: unused `settings` import in `back-end/app/api/portfolio.py`. This has now been fixed on `security/tenant-isolation`; a new CI result is pending.
- Portfolio and snipe-target ownership was a cross-user data isolation risk. A migration, user-scoped model fields, scoped routes, and an isolation regression test are implemented on `security/tenant-isolation`.
- The ownership migration refuses to guess when legacy rows exist with multiple users; if exactly one user exists, legacy rows are assigned to that user. This is deliberately fail-safe.
- Auction tasks remain fail-closed in paper mode; live purchase/bid/listing/email operations remain unauthorized.
- Paper-ledger exposure accounting includes renewals; regression tests are awaiting green CI.
- Remaining preliminary deployment/security concerns include hardcoded database credentials in Docker Compose, database/Redis ports exposed by compose configuration, HTTP-only Nginx configuration, and a cookie security setting that needs review.
- Valuation still lacks reliable comparable completed sales, validated sale probabilities, and a robust buyer-demand signal. Scrapers and marketplace adapters require terms/access/data-quality review.

## Immediate next actions

1. Verify the CI rerun after the Ruff fix.
2. Fix any subsequent test or migration failure from actual CI logs.
3. Merge tenant isolation only after CI and migration checks pass.
4. Audit worker/background-job lookups for owner scoping.
5. Build the deterministic paper-trading discovery-to-exit scenario.
6. Keep real purchase, bid, listing, and email operations disabled until test, security, and explicit-authorization gates are satisfied.

## Acceptance gates before a first usable paper-trading test

- [ ] Reproducible backend startup and database migrations.
- [ ] Ruff and the complete pytest suite pass.
- [ ] Paper mode cannot invoke real purchase, bid, paid-listing, or email-send actions.
- [ ] Per-domain €100 and portfolio €500 limits plus €500 reserve are enforced deterministically.
- [ ] Every recommendation records evidence, assumptions, costs, confidence, and reason.
- [ ] A simulated discovery-to-exit scenario can be replayed and audited.
- [ ] Cash, positions, renewals, fees, and profit/loss reconcile.
- [x] Portfolio and auction/watch records have user ownership fields and scoped API queries (verification pending).
- [ ] Dashboard distinguishes simulated data/results from verified real-world outcomes.

## Progress log

### 2026-10-09 — CI lint failure diagnosed and fixed
- Inspected the latest PR CI run rather than guessing from source.
- Dependency installation succeeded.
- Ruff failed on exactly one issue: unused `app.config.settings` import in `app/api/portfolio.py`.
- Removed the unused import; the branch now needs a fresh CI run to verify the fix.

### 2026-10-09 — Tenant-isolation implementation
- Added `user_id` ownership to portfolio and snipe-target models with foreign keys to `users`.
- Added Alembic migration `0005_scope_user_records.py` with conservative legacy-row handling.
- Scoped portfolio list/create/delete queries to the authenticated user.
- Scoped snipe list/create/delete/trigger queries to the authenticated user.
- Added a regression test proving two users can hold the same domain/watch name without seeing each other's records.

### 2026-10-09 — Paper mode and exposure safety improvements
- Added `TRADING_MODE=paper` as the default and a second explicit `LIVE_TRADING_ENABLED=false` gate.
- The auction worker returns without contacting GoDaddy unless both live flags are explicitly enabled.
- Snipe creation does not queue a bid in paper mode.
- Manual trigger returns an explicit paper-mode response without enqueueing marketplace activity.
- Added per-domain maximum bid input validation of €100.
- Paper-ledger exposure includes renewals and rejects cap violations.

### 2026-10-09 — CI dependency and import-cycle fixes
- Added pinned SQLAlchemy and Alembic after CI exposed missing dependencies.
- Extracted the shared rate limiter to `app/core/rate_limit.py` after test collection exposed a circular import.

### 2026-10-09 — Standalone paper-trading ledger and deterministic investment policy
- Added simulated acquire, renew, and sell operations, transaction records, marketplace fee accounting, and no external side effects.
- Added deterministic BUY_CANDIDATE / WATCH / REJECT recommendations with expected net profit/ROI, renewal costs, maximum bid, confidence, trademark-risk checks, and budget guardrails.

### 2026-10-09 — Project tracking initialized
- Added ROADMAP.md and this status tracker.

## Update protocol

1. Update date, phase, evidence, blockers, and next actions each work session.
2. Record exact tests/checks and actual results.
3. Adjust percentages only when evidence supports the change.
4. Never claim a deployment, integration, test, or background task succeeded unless it was executed and verified.
