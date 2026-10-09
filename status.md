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
| Production readiness | ~28% | Tenant isolation implementation is now in review; CI verification remains open |
| Overall target-product completion | ~22% | Current code is not yet verified end-to-end |

**Current phase:** Phase 1 — Safety foundation; Phase 0 audit remains open  
**Trading mode:** Paper trading only  
**Initial planning capital:** €1,000 EUR  
**Paper limits:** €100 maximum all-in per domain; €500 maximum deployed exposure; €500 reserve  
**Real purchases, bids, paid listings, and outbound email:** Not authorized. Live bidding fails closed unless both `TRADING_MODE=live` and `LIVE_TRADING_ENABLED=true` are configured; the default remains paper mode.

Percentages are engineering estimates, not test results. A commit is not considered verified until CI or a documented local check passes.

## Current blockers and known risks

- Latest confirmed CI result before the tenant-isolation changes: Ruff passed, but pytest collection failed due to a circular import. The limiter has been extracted to `app/core/rate_limit.py`; subsequent CI is pending.
- Portfolio and snipe-target ownership was a cross-user data isolation risk. A migration, user-scoped model fields, scoped portfolio routes, scoped snipe routes, and an isolation regression test have now been implemented on branch `security/tenant-isolation`; CI and migration execution are still pending.
- The ownership migration refuses to guess when legacy rows exist with multiple users; if exactly one user exists, legacy rows are assigned to that user. This is deliberately fail-safe.
- Auction tasks remain fail-closed in paper mode; live purchase/bid/listing/email operations remain unauthorized.
- Paper-ledger exposure accounting includes renewals; regression tests are awaiting green CI.
- Remaining preliminary deployment/security concerns include hardcoded database credentials in Docker Compose, database/Redis ports exposed by compose configuration, HTTP-only Nginx configuration, and a cookie security setting that needs review.
- Valuation still lacks reliable comparable completed sales, validated sale probabilities, and a robust buyer-demand signal. Scrapers and marketplace adapters require terms/access/data-quality review.

## Immediate next actions

1. Run/verify CI against the tenant-isolation branch and fix every failure from actual logs.
2. Merge tenant isolation only after CI and migration checks pass.
3. Add worker-level ownership context wherever background jobs read portfolio/snipe records.
4. Build the first safe paper-trading API and deterministic discovery-to-exit scenario.
5. Keep real purchase, bid, listing, and email operations disabled until test, security, and explicit-authorization gates are satisfied.

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

### 2026-10-09 — Tenant-isolation implementation
- Added `user_id` ownership to portfolio and snipe-target models with foreign keys to `users`.
- Added Alembic migration `0005_scope_user_records.py` with conservative legacy-row handling: one existing user permits deterministic backfill; multiple users plus legacy rows abort rather than guessing ownership.
- Scoped portfolio list/create/delete queries to the authenticated user.
- Scoped snipe list/create/delete/trigger queries to the authenticated user.
- Added a regression test proving two users can hold the same domain/watch name without seeing each other's records.
- Changes are on branch `security/tenant-isolation`; verification is intentionally still pending.

### 2026-10-09 — Paper mode and exposure safety improvements (verification pending)
- Added `TRADING_MODE=paper` as the default and a second explicit `LIVE_TRADING_ENABLED=false` gate. The auction worker now returns without contacting GoDaddy unless both live flags are explicitly enabled.
- The snipe API no longer queues a bid when a watch target is created. Manual trigger returns an explicit paper-mode response without enqueueing any marketplace task.
- Added a per-domain maximum bid input validation of €100; this is only a request validation and does not replace the investment policy.
- Corrected paper-ledger exposure to include renewals already paid; renewal is rejected if it would exceed the deployed-capital limit.

### 2026-10-09 — CI dependency and import-cycle fixes (verification pending)
- CI passed Ruff but failed test collection because SQLAlchemy was missing from `back-end/requirements.txt`; added pinned SQLAlchemy and Alembic.
- The next run then reached test collection and exposed a circular import between `app.main` and `app.api.auth` through the rate limiter. Extracted the shared limiter into `app/core/rate_limit.py` and updated both imports.

### 2026-10-09 — Standalone paper-trading ledger and deterministic investment policy
- Added `back-end/app/services/paper_trading.py` with immutable simulated acquire, renew, and sell operations, transaction records, marketplace fee accounting, and no external side effects.
- Added `back-end/app/services/investment_policy.py` with deterministic BUY_CANDIDATE / WATCH / REJECT recommendations, expected net profit/ROI, renewal costs, maximum bid, confidence and trademark-risk checks, and budget guardrails.

### 2026-10-09 — Project tracking initialized
- Added ROADMAP.md and this status tracker to document phases, safety rules, blockers, and acceptance gates.

## Update protocol

1. Update date, phase, evidence, blockers, and next actions each work session.
2. Record exact tests/checks and actual results.
3. Adjust percentages only when evidence supports the change.
4. Never claim a deployment, integration, test, or background task succeeded unless it was executed and verified.
