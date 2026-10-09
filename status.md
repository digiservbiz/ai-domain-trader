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
| Autonomous investment intelligence | ~25% | Deterministic investment-policy engine added; evidence sources, orchestration, and learning remain incomplete |
| Production readiness | ~30% | Rough estimate; CI/security/deployment issues remain |
| Overall target-product completion | ~18% | Initial deterministic policy engine and unit-test file added; runtime validation is still outstanding |

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
- The latest CI run previously observed had a lint step fail and tests were skipped. Its expired logs could not be retrieved, so the exact failure still needs to be reproduced. Do not assume tests pass.
- Scrapers and marketplace adapters need verification for current provider terms, reliability, data quality, and API access.

These are preliminary findings, not a completed runtime/security audit.

## Immediate next actions

1. Validate the new investment-policy module and its tests in a clean checkout; fix lint/test failures.
2. Reproduce the existing CI lint failure and run the full backend test suite.
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

### 2026-10-09 — First implementation milestone: deterministic investment policy
- Added `back-end/app/services/investment_policy.py`: pure decision engine for BUY_CANDIDATE / WATCH / REJECT, estimated net profit/ROI, renewal costs, maximum permitted bid, evidence confidence, trademark-risk handling, and deterministic per-domain/portfolio caps.
- Added `back-end/tests/test_investment_policy.py` covering a positive paper candidate, high trademark risk, budget/exposure limits, low-confidence evidence, invalid inputs, and maximum bid constraints.
- The evaluator has no network, database, payment, bidding, listing, or email side effects; results explicitly state paper trading only and purchase not executed.
- Tests and lint were not run in this session because no repository checkout/runtime was available through the GitHub file-edit operation. The test suite must be executed before this milestone can be considered validated.

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
