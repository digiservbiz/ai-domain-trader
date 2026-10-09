# AI Domain Trader — Status & Progress

Last updated: 2026-10-09
Repository: https://github.com/digiservbiz/ai-domain-trader
Branch: `security/tenant-isolation`
Draft PR: https://github.com/digiservbiz/ai-domain-trader/pull/1
Roadmap: ROADMAP.md

## Current snapshot

| Measure | Current status | Notes |
|---|---:|---|
| Roadmap and project tracking | 100% | Roadmap and status tracker committed |
| Repository audit | ~88% | Runtime, migration, and deployment validation remain open |
| Existing foundation usefulness | ~49% | Engineering estimate, not a test result |
| Autonomous investment intelligence | ~36% | Policy, paper ledger, lifecycle scenario, audit hashing, and audit persistence API exist; learning/orchestration remain incomplete |
| Production readiness | ~32% | Tenant-scoping and audit persistence committed; latest head needs CI and migration verification |
| Overall target-product completion | ~26% | Estimate only; not verified end-to-end or release readiness |

**Current phase:** Phase 1 — Safety foundation and auditable decisions  
**Trading mode:** Paper trading only  
**Initial planning capital:** €1,000 EUR  
**Paper limits:** €100 maximum all-in per domain; €500 maximum deployed exposure; €500 reserve  
**Real purchases, bids, paid listings, and outbound email:** Not authorized. Live bidding remains fail-closed unless both `TRADING_MODE=live` and `LIVE_TRADING_ENABLED=true` are configured.

Percentages are engineering estimates, not test results. A commit is not considered verified until CI or a documented local check passes.

## Verification state

- CI run #78 (ID `37971601098`) completed successfully on an earlier commit. It does not verify the newer audit-persistence changes.
- Earlier run `37971419652`: Ruff passed; pytest reported 48 passed / 1 failed. The remaining paper-mode test invocation was subsequently corrected.
- Latest known deployment-preparation commit before this status update: `1e4225e5202c07044d994f050875135bad07d937`. The GitHub connector returned no workflow run for the earlier queried head; CI has now been configured to run on pushes to `security/**`, and the new run still needs verification.
- Alembic migrations `0005` and `0006` have not yet been executed against SQLite and the intended production database dialect.

## Implemented

- Deterministic candidate policy and paper ledger with acquisition, renewals, sale, fees, exposure limits, and reconciliation.
- Candidate-to-exit paper scenario runner and regression tests.
- SHA-256 decision snapshots with normalized domain, financials, policy, reasons, and evidence provenance.
- Persistent `decision_audits` model and Alembic migration `0006_persist_decision_audits`.
- Authenticated `POST /decision-audits`, `GET /decision-audits`, and `GET /decision-audits/{audit_id}` endpoints.
- SQLite-backed model persistence test and endpoint-level tests for persistence, idempotency, list/retrieve, same-content hashes across users, and private-record isolation.
- Portfolio and snipe-target ownership fields, user-scoped CRUD/trigger routes, conservative legacy migration, and worker lookup by persisted target ID.
- Paper mode fails closed before marketplace bidding; real-world actions remain unauthorized.

## Current blockers and known risks

1. Verify CI on current head and fix failures based on actual logs.
2. Execute full Alembic upgrade/downgrade chain against SQLite and validate the production dialect. Migration `0005` intentionally aborts if legacy record ownership is ambiguous.
3. Connect discovery, SEO/trend signals, valuation, policy, paper scenario, and persisted audit into a reproducible pipeline.
4. Build historical-sales ingestion and evaluation; distinguish completed-sale evidence from asking prices and estimates.
5. Harden deployment: the Render test blueprint is added and production login cookies now use `COOKIE_SECURE=true`; frontend deployment/CORS configuration and production-database migration validation remain open. Existing Docker Compose still has hardcoded database credentials and exposed database/Redis ports.
6. Review scraper and marketplace adapter terms, reliability, provenance, and rate limits.

## Immediate next actions

1. Check the newest CI run for the current PR head and inspect failures.
2. Validate migration upgrade/downgrade with disposable databases.
3. Implement the deterministic discovery → evidence → valuation → paper decision → audit pipeline.
4. Add historical-sales learning with provenance and quality checks.
5. Finish Render API deployment, then connect the frontend using its real API URL and exact CORS origin.
6. Keep real purchases, bids, paid listings, and email sending disabled until safety gates pass and explicit authorization is provided.

## Acceptance gates before a first usable paper-trading test

- [ ] Reproducible backend startup and complete database migrations.
- [ ] Ruff and complete pytest suite pass on the current branch.
- [ ] Paper mode cannot invoke real purchase, bid, paid-listing, or email-send actions.
- [ ] €100 per-domain and €500 deployed-capital limits plus €500 reserve are enforced deterministically.
- [ ] Every recommendation stores evidence, assumptions, costs, confidence, and reasons.
- [ ] A simulated discovery-to-exit scenario can be replayed and audited.
- [ ] Cash, positions, renewals, fees, and profit/loss reconcile.
- [x] Portfolio and auction/watch records have owner fields and scoped API queries (full runtime verification outstanding).
- [x] Decision-audit model, migration, and tenant-scoped API endpoints added (current CI/migration verification outstanding).
- [ ] Dashboard distinguishes simulated results from verified real-world outcomes.
- [ ] Production secrets and exposed services are hardened.
- [x] Render API/database blueprint and HTTPS-secure cookie configuration added (deployment not yet run).

## Progress log

### 2026-10-09 — Render test deployment preparation
- Added `render.yaml` for a first API-only Render deployment with a disposable free PostgreSQL database, health check, generated `SECRET_KEY`, production environment, secure cookies, and explicit paper-mode/live-bid-off flags.
- Changed authentication cookie security to default on in production and configurable via `COOKIE_SECURE`; login and logout use the same cookie settings.
- Updated CI push triggers to include `security/**` branches so this working branch can be tested directly.
- No Render service has been created or deployed yet. The frontend is intentionally not in the first blueprint: its public API URL and backend CORS origin must be configured after Render provides the API hostname.
- Latest deployment-preparation commit: `1e4225e5202c07044d994f050875135bad07d937`. CI and database migrations remain unverified.

### 2026-10-09 — Persistent decision audit history
- Added `DecisionAudit` model and migration `0006_persist_decision_audits.py`.
- Added authenticated create/list/retrieve endpoints; stores canonical snapshot JSON and SHA-256 audit ID.
- Same user's repeated submissions are idempotent. Same content hashes can exist independently in different accounts; list/get queries are tenant-scoped.
- Added SQLite-backed persistence test and endpoint-level tests for idempotency, list/retrieve, cross-account duplicate hashes, and hiding private records.
- Registered model with Alembic metadata and router with FastAPI.
- Latest code commit: `39301bf629fab8b5a9a88c26f8ca25aa2de7b9a9`. No CI status was returned for this head at update time.

### 2026-10-09 — CI follow-up and deterministic audit snapshots
- Run `37971298543`: Ruff and dependency installation passed; pytest reported 44 passed and 2 failed because a Celery task test supplied the target ID twice.
- Run `37971419652`: Ruff passed; pytest reported 48 passed and 1 failed; the remaining paper-mode invocation was corrected afterward.
- Earlier CI run #78 passed on an earlier commit, not on the audit-persistence changes.
- Added deterministic SHA-256 audit snapshots and evidence provenance with stability and validation tests.

### 2026-10-09 — Paper scenario and worker safety
- Added deterministic candidate-to-paper-acquisition-to-renewal-to-sale scenario with reconciliation tests.
- Auction worker now receives a persisted target ID, reloads its domain and bid cap, and updates only that row. Paper mode exits before database or marketplace actions.

### 2026-10-09 — Tenant isolation and paper policy
- Added owner IDs and scoped portfolio/snipe routes, plus a conservative legacy migration.
- Added paper-only defaults, explicit second live-bidding gate, bid cap validation, deterministic BUY_CANDIDATE/WATCH/REJECT policy, exposure accounting, and simulated ledger.

## Update protocol

1. Update date, phase, evidence, blockers, and next actions each work session.
2. Record exact tests/checks and actual results.
3. Adjust percentages only when evidence supports the change.
4. Never claim a deployment, integration, test, or background task succeeded unless it was executed and verified.

### 2026-10-09 — Render deployment migration-chain fix
- First Render build completed, but startup failed during `alembic upgrade head`: migration `0005_scope_user_records` referenced `0004_create_snipe_targets_table`, while the actual migration declares its revision ID as `0004`.
- Corrected `back-end/alembic/versions/0005_scope_user_records.py` so its `down_revision` points to the actual existing revision ID `0004`.
- Fix committed to `security/tenant-isolation`; redeployment and full migration execution are still required. Do not treat the deployment as healthy until Render starts the API and `/healthz` succeeds.

### 2026-10-09 — Render deployment completed; CI uncovered audit-list default bug
- User confirmed Render shows both deployments for commits `7e96306` and `33885c4` as **Deployed**. This confirms deployment completion, but API health and database migration success still need runtime verification.
- Inspected GitHub Actions CI run #97 (run ID `37975286507`): lint passed; pytest result was **50 passed, 2 failed**.
- Both failures were in `tests/test_decision_audit_api.py`: direct calls to `list_decision_audits()` received FastAPI `Query` objects as defaults, causing SQLAlchemy offset conversion to raise `TypeError`.
- Fixed the endpoint signature with `Annotated[int, Query(...)]` metadata and plain Python defaults (`limit=20`, `offset=0`); committed as `aba8041981c73e8dfd9b4a4ddbb77b12b4ed1345`.
- Next: rerun CI on the updated branch, verify the newest Render deployment logs show all migrations through `0006` succeeded, and test `/healthz`. Do not mark production readiness complete until these checks pass.
