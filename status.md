# AI Domain Trader — Status & Progress

Last updated: 2026-10-09
Repository: https://github.com/digiservbiz/ai-domain-trader
Roadmap: ROADMAP.md

## Current snapshot

| Measure | Current status | Notes |
|---|---:|---|
| Roadmap and project tracking | 100% | ROADMAP.md and this status file committed to the repository |
| Repository audit | ~80% | Preliminary source review; several checks still need reproduction/runtime validation |
| Existing foundation usefulness | ~45% | Rough engineering estimate, not a test result |
| Autonomous investment intelligence | ~28% | Policy engine and isolated paper-trading ledger added; evidence sources, orchestration, and learning remain incomplete |
| Production readiness | ~30% | Rough estimate; CI/security/deployment issues remain |
| Overall target-product completion | ~21% | Deterministic policy engine and standalone paper ledger added; CI tests still need to pass |

**Current phase:** Phase 1 — Safety foundation (started); Phase 0 audit remains open  
**Trading mode:** Paper trading only  
**Initial planning capital:** €1,000 EUR  
**Suggested paper limits:** €100 maximum all-in per domain; €500 maximum deployed exposure; €500 reserve  
**Real purchases, bids, paid listings, and outbound email:** Not authorized; must remain disabled in paper mode.

Percentages are estimates and will change only when evidence supports the change. Code existing in the repository does not by itself count as a verified, completed feature.

## Known findings from the preliminary source review

- The repository has a FastAPI backend, PostgreSQL/Alembic, Redis/Celery jobs, and a Next.js frontend.
- Domain discovery, basic name generation/valuation, trend/scraping tasks, portfolio endpoints, and some marketplace/auction integrations exist.
- Valuation is currently simplistic and does not yet combine reliable comparable completed sales, probability of sale, total ownership costs, and buyer demand into a robust investment decision.
- Auction logic needs stronger expected-value, all-in-cost, exposure, and emergency-stop controls before any live execution.
- Preliminary deployment/security concerns include hardcoded database credentials in Docker Compose, database/Redis ports exposed by the compose configuration, HTTP-only Nginx configuration, and a cookie security setting that needs review.
- CI confirmed Ruff lint now passes on commit `3cd4fff`. The test step then failed before collection because `SECRET_KEY` was not set in the CI environment. The workflow now supplies a disposable CI-only test secret; a new run is pending. The paper-trading ledger and its tests were added afterward, so those new files are not yet verified by CI.
- Scrapers and marketplace adapters need verification for current provider terms, reliability, data quality, and API access.

These are preliminary findings, not a completed runtime/security audit.

## Immediate next actions

1. Confirm CI passes lint and executes the complete suite with the test-only secret; fix any remaining failures.
2. Validate the paper-ledger accounting and reserve-capital edge cases in CI.
3. Inspect migrations and confirm data models support per-user isolation for portfolios and auction targets.
4. Trace API authorization and live-action paths, including the auction sniper and marketplace adapters.
5. Wire the policy engine into a safe paper-trading API/workflow after verifying how user portfolio exposure is calculated.
6. Add the paper ledger and deterministic end-to-end scenario.
7. Keep all live-money and outbound-email behavior disabled until the paper-trading acceptance criteria are met.

## Acceptance gates before a first usable paper-trading test

- [ ] Project starts using documented, reproducible setup steps.
- [ ] Lint and tests run; failures are fixed or clearly documented.
- [ ] Paper mode cannot invoke real purchase, bid, paid-listing, or email-send actions.
- [ ] Per-domain €100 and portfolio €500 limits are enforced in deterministic code.
- [ ] Every recommendation records evidence, assumptions, costs, confidence, and a decision reason.
- [ ] A complete simulated discovery-to-exit scenario can be replayed and audited.
- [ ] Cash, simulated positions, renewals, fees, and profit/loss reconcile.
- [ ] Dashboard clearly labels simulated vs verified real-world data and outcomes.

## Progress log

### 2026-10-09 — Standalone paper-trading ledger
- Added `back-end/app/services/paper_trading.py` with immutable account/position/transaction records and simulated acquire, renew, and sell operations.
- The ledger enforces per-domain all-in cost, portfolio exposure, and reserve cash limits; records marketplace fees and realized profit/loss; explicitly labels transactions as simulated; and has no payment, registrar, marketplace, or email side effects.
- Added `back-end/tests/test_paper_trading.py` for round-trip accounting, fees, reserve/domain caps, duplicates, invalid inputs, and unknown positions. Tests are awaiting CI verification.

### 2026-10-09 — CI lint repair and reserve-capital guardrail
- Retrieved the CI job log: Ruff reported 10 E402 import-order findings in `app/main.py` caused by Sentry initialization before application imports, plus one E401 multiple-import finding in `app/models/valuation.py`.
- Added targeted `# noqa: E402` annotations to preserve Sentry-before-app-import initialization, and split/normalized imports in the valuation module.
- Updated the policy to reserve €500 of the €1,000 starting capital explicitly; maximum permitted bids now use spendable capital and the policy rejects exposure/reserve combinations that exceed starting capital.
- Added tests for reserve preservation and invalid reserve/exposure configuration.
- Ruff passed in CI, but tests stopped during import because `SECRET_KEY` was missing. Updated `.github/workflows/ci.yml` to provide a disposable test-only key. The next CI run must verify this fix and all tests.

### 2026-10-09 — First implementation milestone: deterministic investment policy
- Added `back-end/app/services/investment_policy.py`: pure decision engine for BUY_CANDIDATE / WATCH / REJECT, estimated net profit/ROI, renewal costs, maximum permitted bid, evidence confidence, trademark-risk handling, and deterministic per-domain/portfolio caps.
- Added `back-end/tests/test_investment_policy.py` covering a positive paper candidate, high trademark risk, budget/exposure limits, low-confidence evidence, invalid inputs, and maximum bid constraints.
- The evaluator has no network, database, payment, bidding, listing, or email side effects; results explicitly state paper trading only and purchase not executed.
- The first CI run failed Ruff lint. The lint findings have been fixed and a subsequent run reported all lint checks passed; tests then exposed a missing CI-only `SECRET_KEY`, now fixed in the workflow. Full test success remains unverified.

### 2026-10-09 — Project tracking initialized
- Added ROADMAP.md with phased delivery plan, architecture, safety rules, and exit criteria.
- Added status.md to track project completion, audit completion, blockers, acceptance gates, and future updates.
- No application code was changed in this step.
- No tests, lint commands, or runtime checks were run in this step.
- Next: continue Phase 0 audit and reproduce the CI lint failure.

## Update protocol

Every meaningful work session must update this file:
1. Change the last-updated date and current phase.
2. Record completed work with links/files and evidence.
3. Record exact tests/checks run and their actual outcomes.
4. Adjust percentages only when verified progress warrants it.
5. Keep blockers and next actions short and concrete.
6. Never claim a deployment, test, integration, or background task succeeded unless it was actually executed and verified.
