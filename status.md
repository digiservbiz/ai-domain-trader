# AI Domain Trader — Status & Progress

Last updated: 2026-10-09
Repository: https://github.com/digiservbiz/ai-domain-trader
Roadmap: ROADMAP.md

## Current snapshot

| Measure | Current status | Notes |
|---|---:|---|
| Roadmap and project tracking | 100% | ROADMAP.md and this status file committed |
| Repository audit | ~80% | Preliminary source review; runtime/security validation remains open |
| Existing foundation usefulness | ~45% | Rough engineering estimate, not a test result |
| Autonomous investment intelligence | ~28% | Policy engine and isolated paper ledger exist; data evidence, orchestration, and learning remain incomplete |
| Production readiness | ~25% | Rough estimate; security, tenant isolation, and test-suite blockers remain |
| Overall target-product completion | ~21% | Current code is not yet verified end-to-end |

**Current phase:** Phase 1 — Safety foundation; Phase 0 audit remains open  
**Trading mode:** Paper trading only  
**Initial planning capital:** €1,000 EUR  
**Paper limits:** €100 maximum all-in per domain; €500 maximum deployed exposure; €500 reserve  
**Real purchases, bids, paid listings, and outbound email:** Not authorized. Live bidding now fails closed unless both `TRADING_MODE=live` and `LIVE_TRADING_ENABLED=true` are configured; the default remains paper mode.

Percentages are engineering estimates, not test results. A commit is not considered verified until CI or a documented local check passes.

## Current blockers and known risks

- Latest confirmed CI result before the newest changes: Ruff passed, but pytest collection failed due to a circular import (`app.api.auth` imported `limiter` from partially initialized `app.main`). The limiter has been extracted to `app/core/rate_limit.py`; subsequent CI is pending.
- SQLAlchemy and Alembic were missing from backend requirements and have been added with pinned versions. CI then advanced to test collection and exposed the circular import above.
- Existing portfolio and snipe-target records are not scoped to the authenticated user. This is a cross-user data isolation risk and must be fixed before exposing those routes beyond controlled testing.
- Auction tasks previously made a live GoDaddy bid request whenever credentials existed. Added a fail-closed trading-mode check in the Celery task, disabled auto-queueing when a watch target is created, and made trigger responses explicitly report that no action was queued in paper mode. These changes await CI verification.
- Paper-ledger exposure accounting now counts carrying cost including renewals; renewal operations reject exposure-cap violations. Regression tests were added but await CI verification.
- Remaining preliminary deployment/security concerns include hardcoded database credentials in Docker Compose, database/Redis ports exposed by compose configuration, HTTP-only Nginx configuration, and a cookie security setting that needs review.
- Valuation still lacks reliable comparable completed sales, validated sale probabilities, and a robust buyer-demand signal. Scrapers and marketplace adapters require terms/access/data-quality review.

## Immediate next actions

1. Get the complete CI suite green and fix each failure based on actual logs.
2. Add tests proving the default trading mode cannot place live bids.
3. Implement per-user ownership and database migration for portfolio and snipe targets; scope all reads, writes, deletes, and worker lookups to the owner.
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
- [ ] Portfolio and auction records are user-scoped.
- [ ] Dashboard distinguishes simulated data/results from verified real-world outcomes.

## Progress log

### 2026-10-09 — Paper mode and exposure safety improvements (verification pending)
- Added `TRADING_MODE=paper` as the default and a second explicit `LIVE_TRADING_ENABLED=false` gate. The auction worker now returns without contacting GoDaddy unless both live flags are explicitly enabled.
- The snipe API no longer queues a bid when a watch target is created. Manual trigger returns an explicit paper-mode response without enqueueing any marketplace task.
- Added a per-domain maximum bid input validation of €100; this is only a request validation and does not replace the investment policy.
- Corrected paper-ledger exposure to include renewals already paid; renewal is rejected if it would exceed the deployed-capital limit. Added a regression test for this case.
- These code changes and tests are committed; latest CI checks are still running and no pass is claimed yet.

### 2026-10-09 — CI dependency and import-cycle fixes (verification pending)
- CI passed Ruff but failed test collection because SQLAlchemy was missing from `back-end/requirements.txt`; added pinned SQLAlchemy and Alembic.
- The next run then reached test collection and exposed a circular import between `app.main` and `app.api.auth` through the rate limiter. Extracted the shared limiter into `app/core/rate_limit.py` and updated both imports.
- Latest related CI run: https://github.com/digiservbiz/ai-domain-trader/actions/runs/37895201103. Full test success remains unverified.

### 2026-10-09 — Standalone paper-trading ledger and deterministic investment policy
- Added `back-end/app/services/paper_trading.py` with immutable simulated acquire, renew, and sell operations, transaction records, marketplace fee accounting, and no external side effects.
- Added `back-end/app/services/investment_policy.py` with deterministic BUY_CANDIDATE / WATCH / REJECT recommendations, expected net profit/ROI, renewal costs, maximum bid, confidence and trademark-risk checks, and budget guardrails.
- Added tests for policy decisions, accounting, caps, reserve cash, duplicates, invalid inputs, and missing positions. These are awaiting green CI.

### 2026-10-09 — Project tracking initialized
- Added ROADMAP.md and this status tracker to document phases, safety rules, blockers, and acceptance gates.
- No runtime/deployment success is claimed without actual verification.

## Update protocol

1. Update date, phase, evidence, blockers, and next actions each work session.
2. Record exact tests/checks and actual results.
3. Adjust percentages only when evidence supports the change.
4. Never claim a deployment, integration, test, or background task succeeded unless it was executed and verified.
