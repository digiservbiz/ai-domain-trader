# AI Domain Trader — Status & Progress

Last updated: 2026-10-09
Repository: https://github.com/digiservbiz/ai-domain-trader
Roadmap: ROADMAP.md

## Current snapshot

| Measure | Current status | Notes |
|---|---:|---|
| Roadmap and project tracking | 100% | ROADMAP.md and this status file committed |
| Repository audit | ~88% | Worker ownership lookup reviewed and corrected; runtime/migration validation remains open |
| Existing foundation usefulness | ~47% | Rough engineering estimate, not a test result |
| Autonomous investment intelligence | ~32% | Policy engine, paper ledger, lifecycle simulation, and deterministic decision-audit snapshots exist; persistence, orchestration, and learning remain incomplete |
| Production readiness | ~31% | Tenant-scoping and worker lookup fixes committed on the security branch; latest test fix awaits CI |
| Overall target-product completion | ~24% | Not verified end-to-end; this is not a release-readiness score |

**Current phase:** Phase 1 — Safety foundation; Phase 0 audit remains open  
**Trading mode:** Paper trading only  
**Initial planning capital:** €1,000 EUR  
**Paper limits:** €100 maximum all-in per domain; €500 maximum deployed exposure; €500 reserve  
**Real purchases, bids, paid listings, and outbound email:** Not authorized. Live bidding fails closed unless both `TRADING_MODE=live` and `LIVE_TRADING_ENABLED=true` are configured; the default remains paper mode.

Percentages are engineering estimates, not test results. A commit is not considered verified until CI or a documented local check passes.

## Current blockers and known risks

- CI run `37971419652` confirmed Ruff and dependency installation pass, and the live-enabled auction worker test plus all three decision-audit tests passed. Pytest reported **48 passed, 1 failed** because the paper-mode test retained an old bound-task invocation.
- Corrected the remaining call to `auction.snipe.run(target_id=22)` in commit `2dfd8f9c72cd38975fd142e012061e4c428a2354`. Latest commit is on the open draft PR; a fresh green CI run is still required.
- Added `app/services/decision_audit.py`, a storage-agnostic SHA-256 audit snapshot with normalized domain, policy inputs, financials, reasons, and evidence provenance. Added tests for stable IDs, evidence-sensitive hashes, and validation. This is not database persistence yet.
- Portfolio and snipe-target ownership was a cross-user data isolation risk. A migration, user-scoped model fields, scoped routes, and an isolation regression test are implemented on `security/tenant-isolation`.
- The ownership migration refuses to guess when legacy rows exist with multiple users; if exactly one user exists, legacy rows are assigned to that user. This is deliberately fail-safe.
- Auction tasks remain fail-closed in paper mode; live purchase/bid/listing/email operations remain unauthorized.
- Worker lookup previously selected watch records by domain only, which could update another user's row when multiple users watch the same domain. The task now receives a unique target ID, loads the persisted domain and max bid from that row, and updates only that row. The API queues by target ID.
- Remaining preliminary deployment/security concerns include hardcoded database credentials in Docker Compose, database/Redis ports exposed by compose configuration, HTTP-only Nginx configuration, and a cookie security setting that needs review.
- Valuation still lacks reliable comparable completed sales, validated sale probabilities, and a robust buyer-demand signal. Scrapers and marketplace adapters require terms/access/data-quality review.

## Immediate next actions

1. Recheck CI for the test fix and resolve any new failures from actual logs.
2. Verify the ownership migration against SQLite and the production database dialect before merging.
3. Persist decision-audit snapshots in the database with migrations and retrieval endpoints.
4. Connect discovery, SEO/trend signals, valuation, and the paper scenario in a reproducible pipeline.
5. Harden deployment configuration and provide repeatable VPS setup checks.
6. Keep real purchase, bid, listing, and email operations disabled until tests, security gates, and explicit authorization are satisfied.

## Acceptance gates before a first usable paper-trading test

- [ ] Reproducible backend startup and database migrations.
- [ ] Ruff and the complete pytest suite pass on the current branch.
- [ ] Paper mode cannot invoke real purchase, bid, paid-listing, or email-send actions.
- [ ] Per-domain €100 and portfolio €500 limits plus €500 reserve are enforced deterministically.
- [ ] Every recommendation records evidence, assumptions, costs, confidence, and reason.
- [ ] A simulated discovery-to-exit scenario can be replayed and audited.
- [ ] Cash, positions, renewals, fees, and profit/loss reconcile.
- [x] Portfolio and auction/watch records have user ownership fields and scoped API queries (automated verification still required).
- [ ] Dashboard distinguishes simulated data/results from verified real-world outcomes.
- [ ] Production deployment secrets and exposed services are hardened.

## Progress log

### 2026-10-09 — CI follow-up and deterministic audit snapshots
- Run `37971298543`: Ruff and dependency installation passed; pytest reported 44 passed and 2 failed because the Celery task test invocation supplied the target ID twice.
- Run `37971419652`: Ruff passed; pytest improved to 48 passed and 1 failed. The remaining failure was a second test call not changed by the first fix.
- Corrected that remaining call in commit `2dfd8f9c72cd38975fd142e012061e4c428a2354`; CI for the latest head is not yet confirmed green.
- Added deterministic decision audit snapshots with SHA-256 content IDs and source provenance fields, plus regression tests. Commits: `818db51136dca442449751c3ce8a8d6e2e5dfd89` and `4eb6c388721a8efd9ba2a88cd434dd0f15612ba3`.
- Audit snapshots are currently in-memory return values; database persistence and UI history are still outstanding.

### 2026-10-09 — End-to-end paper scenario
- Added a deterministic candidate-to-paper-acquisition-to-renewal-to-sale scenario runner and reconciliation report.
- Added tests for a complete simulated lifecycle, a WATCH stop, and invalid inputs.
- This uses only the pure paper ledger; it does not buy domains or contact marketplaces/buyers.

### 2026-10-09 — Background worker ownership fix
- Changed the auction task contract to accept a watch-target primary key instead of a domain string and caller-supplied bid amount.
- Added tests for persisted target ID/bid cap usage and proving paper mode exits before database or marketplace calls.
- The worker reloads the persisted target and bid cap, then updates only that row; same-domain watches owned by different users cannot collide during status updates.
- Updated the API trigger and scheduled runner to enqueue target IDs.

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
