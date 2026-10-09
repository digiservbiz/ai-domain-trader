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
| Autonomous investment intelligence | ~36% | Policy, paper ledger, lifecycle scenario, audit hashing, and audit persistence API now exist; learning/orchestration remain incomplete |
| Production readiness | ~32% | Tenant-scoping and audit persistence changes are committed; latest head still needs CI and migration verification |
| Overall target-product completion | ~26% | Engineering estimate; not verified end-to-end or release readiness |

**Current phase:** Phase 1 — Safety foundation and auditable decisions  
**Trading mode:** Paper trading only  
**Initial planning capital:** €1,000 EUR  
**Paper limits:** €100 maximum all-in per domain; €500 maximum deployed exposure; €500 reserve  
**Real purchases, bids, paid listings, and outbound email:** Not authorized. Live bidding remains fail-closed unless both `TRADING_MODE=live` and `LIVE_TRADING_ENABLED=true` are configured.

Percentages are engineering estimates, not test results. A commit is not considered verified until CI or a documented local check passes.

## Verified checks and current verification state

- CI run #78 (run ID `37971601098`) completed successfully on an earlier commit. This does not validate the audit-persistence changes added afterward.
- The last previously documented failing run (`37971419652`) had Ruff pass and pytest report 48 passed / 1 failed. The remaining test invocation was corrected afterward; that older run must not be treated as the latest result.
- The current PR head includes audit persistence model, migration, API endpoints, and an initial database isolation test. No CI status was returned for current head `0c30ba06f8e7428ced625a283f0040e1cd42dba9` at the time of this update; run current CI before claiming the latest code passes.
- SQLite/production-dialect execution of migrations `0005` and `0006` is not yet verified.

## Implemented

- Deterministic candidate policy and simulated paper ledger with acquisition, renewals, sale, fees, limits, and reconciliation.
- Candidate-to-exit paper scenario runner and regression tests.
- SHA-256 decision audit snapshots with normalized domain, inputs, financials, policy, reasons, and evidence provenance.
- Persistent `decision_audits` model and Alembic migration `0006_persist_decision_audits`.
- Authenticated `/decision-audits` endpoints to create, list, and retrieve records. Reads and idempotency checks are scoped to the authenticated user; the same content hash may exist in different accounts.
- Portfolio and snipe-target ownership fields, user-scoped CRUD/trigger routes, conservative legacy migration, and worker lookup by persisted target ID.
- Paper mode fails closed before marketplace bidding; live actions remain unauthorized.

## Current blockers and known risks

1. Verify CI on the current branch head and fix failures from actual logs.
2. Run the full Alembic chain against SQLite and validate behavior against the intended production database dialect. Migration `0005` intentionally aborts if legacy records have ambiguous ownership.
3. Expand endpoint-level tests for audit creation, idempotency, listing, retrieval, invalid payloads, and cross-user isolation.
4. Connect discovery, SEO/trend signals, valuation, policy, paper scenario, and persisted audit into one reproducible pipeline.
5. Build learning from historical domain sales; avoid treating asking prices or unverified marketplace estimates as completed-sale evidence.
6. Harden deployment: Docker Compose has known concerns around hardcoded database credentials and exposed database/Redis ports; Nginx is HTTP-only; cookie secure settings need review.
7. Review third-party scraping/marketplace adapter terms, reliability, provenance, and rate limits before production use.

## Immediate next actions

1. Check the newest CI run for the current PR head and inspect failures.
2. Add route-level persistence and tenant-isolation tests.
3. Validate migration upgrade/downgrade paths with a disposable test database.
4. Implement the deterministic discovery → evidence → valuation → paper decision → audit pipeline.
5. Add historical-sales ingestion and a learning/evaluation dataset with provenance and quality checks.
6. Keep real purchases, bids, paid listings, and email sending disabled until all safety gates pass and explicit authorization is provided.

## Acceptance gates before a first usable paper-trading test

- [ ] Reproducible backend startup and complete database migrations.
- [ ] Ruff and complete pytest suite pass on the current branch.
- [ ] Paper mode cannot invoke real purchase, bid, paid-listing, or email-send actions.
- [ ] €100 per-domain and €500 deployed-capital limits plus €500 reserve are enforced deterministically.
- [ ] Every recommendation stores evidence, assumptions, costs, confidence, and reasons.
- [ ] A simulated discovery-to-exit scenario can be replayed and audited.
- [ ] Cash, positions, renewals, fees, and profit/loss reconcile.
- [x] Portfolio and auction/watch records have owner fields and scoped API queries (full runtime verification still outstanding).
- [x] Decision-audit persistence model, migration, and tenant-scoped API endpoints added (current CI/migration verification outstanding).
- [ ] Dashboard clearly distinguishes simulated results from verified real-world outcomes.
- [ ] Production secrets and exposed services are hardened.

## Progress log

### 2026-10-09 — Persistent decision audit history
- Added `DecisionAudit` SQLAlchemy model and migration `0006_persist_decision_audits.py`, linked after `0005_scope_user_records`.
- Added authenticated `POST /decision-audits`, `GET /decision-audits`, and `GET /decision-audits/{audit_id}` endpoints.
- Stored canonical decision snapshot JSON and SHA-256 audit ID; repeated submissions by the same user are idempotent.
- Scoped history queries and uniqueness to the account; identical content hashes can be stored independently by different users.
- Added a SQLite-backed persistence and ownership test. Endpoint-level tests and current-head CI are still required.
- Registered the audit model with Alembic metadata and the API router with FastAPI.
- Current latest known PR head at update time: `0c30ba06f8e7428ced625a283f0040e1cd42dba9`; no current-head CI status was returned by the connector.

### 2026-10-09 — CI follow-up and deterministic audit snapshots
- Run `37971298543`: Ruff and dependency installation passed; pytest reported 44 passed and 2 failed due to a Celery task invocation passing the target ID twice.
- Run `37971419652`: Ruff passed; pytest reported 48 passed and 1 failed; corrected the remaining paper-mode invocation afterward.
- Earlier CI run #78 (ID `37971601098`) passed on an earlier commit, not on the audit-persistence changes.
- Added deterministic SHA-256 audit snapshots and evidence provenance with tests for stable IDs, evidence-sensitive hashes, and validation.

### 2026-10-09 — End-to-end paper scenario
- Added a deterministic candidate-to-paper-acquisition-to-renewal-to-sale runner and reconciliation report.
- Added tests for completed simulated lifecycle, WATCH stop, and invalid inputs. No real domain purchase or buyer contact occurs.

### 2026-10-09 — Background worker ownership fix
- Auction task accepts a watch-target primary key, reloads persisted domain and bid cap, and updates only that row.
- Added tests for persisted target lookup and paper-mode exit before database or marketplace calls.

### 2026-10-09 — Tenant-isolation implementation
- Added `user_id` ownership to portfolio and snipe-target models and a conservative Alembic migration.
- Scoped portfolio and snipe list/create/delete/trigger operations to the authenticated owner.
- Added a regression test for same-domain records belonging to different users.

### 2026-10-09 — Paper mode and investment policy
- Added paper-only default, explicit second live-bidding gate, per-domain bid-cap validation, deterministic BUY_CANDIDATE/WATCH/REJECT decisions, exposure accounting, and a simulated ledger.

## Update protocol

1. Update date, phase, evidence, blockers, and next actions each work session.
2. Record exact tests/checks and actual results.
3. Adjust percentages only when evidence supports the change.
4. Never claim a deployment, integration, test, or background task succeeded unless it was executed and verified.
