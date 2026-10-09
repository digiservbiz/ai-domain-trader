# AI Domain Trader — Project Roadmap

Last updated: 2026-10-09
Project repository: https://github.com/digiservbiz/ai-domain-trader

## Product goal

Build a reliable, evidence-led AI domain-investment agent that discovers candidate domains, researches quality and resale potential, makes explainable acquisition decisions, simulates the investment lifecycle, identifies likely buyers, manages sales workflows, and learns from verified outcomes.

The system must be useful in paper-trading mode before any live-money capability is enabled. AI recommendations must never override deterministic financial, security, or compliance controls.

## Non-negotiable operating rules

- Initial planning capital: **€1,000 EUR**.
- Initial mode: **paper trading only**.
- Suggested paper-trading limits: maximum all-in acquisition cost of **€100 per domain** and maximum simulated deployed capital of **€500**, leaving a **€500 reserve**. These are configurable policy defaults, not claims of optimal investment performance.
- Paper mode must not place real orders/bids, purchase domains, create paid listings, or send outbound emails.
- Live actions must be disabled by default and require explicit configuration and approval after acceptance tests.
- Keep an auditable ledger of decisions, data sources, assumptions, costs, fees, renewals, offers, and outcomes.
- Clearly distinguish verified completed sales from asking prices, model estimates, and simulated outcomes.
- Reject or hold candidates when evidence is weak, trademark risk is high, costs exceed limits, or portfolio exposure limits are breached.
- Keep operating expenses (data subscriptions, email services, AI/API usage, hosting) separate from the €1,000 acquisition budget.
- Use lawful data access, provider terms, privacy requirements, opt-outs, suppression lists, and conservative email limits.

## Delivery phases

### Phase 0 — Repository audit and baseline
**Status: In progress**
- [ ] Reproduce and document the current CI lint failure.
- [ ] Run tests and record actual results; do not treat unrun tests as passing.
- [ ] Review database migrations, model relationships, and data integrity.
- [ ] Review API authentication, authorization/tenant isolation, rate limiting, CSRF/session settings, and secrets handling.
- [ ] Review valuation logic and its fallback behavior.
- [ ] Review auction/bid code, marketplace adapters, and Celery scheduling.
- [ ] Establish a repeatable local Docker-based validation procedure.
**Exit criteria:** a written audit with reproducible findings, prioritized risks, and a known-good baseline.

### Phase 1 — Safety foundation and reproducible test environment
**Status: Planned**
- [ ] Fix lint and test failures.
- [ ] Remove hardcoded secrets; provide safe environment-variable examples and startup validation.
- [ ] Harden deployment defaults: HTTPS, secure cookies, restricted database/Redis exposure, and safe CORS/headers.
- [ ] Verify authorization and isolate each user's portfolio and trading targets.
- [ ] Add a global kill switch and explicit PAPER / LIVE mode separation.
- [ ] Add structured logs, audit events, and clear failure handling.
**Exit criteria:** repeatable tests pass; unsafe live actions cannot occur in paper mode; security-critical findings are resolved or documented with mitigations.

### Phase 2 — Domain intelligence and evidence database
**Status: Planned**
- [ ] Normalize domains, TLDs, dates, currencies, and source identifiers.
- [ ] Store source, retrieval time, confidence, and evidence for every material metric.
- [ ] Add comparable completed sales where licensing/access permits; separate sale prices from asking prices.
- [ ] Add brandability/name quality, TLD fit, search/trend signals, backlink/referring-domain quality, historical use, spam signals, and trademark-risk checks.
- [ ] Add buyer-demand signals and a confidence score; expose missing data instead of silently inventing values.
- [ ] Cache results, respect provider limits, and track data freshness/cost.
**Exit criteria:** a candidate has an explainable evidence profile and the system labels estimates and uncertainty honestly.

### Phase 3 — Investment decision and portfolio risk engine
**Status: Planned**
- [ ] Estimate a resale range and sale-probability range rather than relying on a single unsupported value.
- [ ] Estimate total cost of ownership: acquisition, marketplace/payment fees, renewals, and relevant operating costs.
- [ ] Calculate expected net return, downside, holding period, and maximum rational bid.
- [ ] Enforce per-domain and portfolio-wide limits in deterministic code, independent of AI output.
- [ ] Produce explainable BUY CANDIDATE, WATCH, or REJECT decisions with reasons and missing evidence.
- [ ] Add duplicate, concentration, liquidity, and renewal-risk controls.
**Exit criteria:** automated tests prove that budget and risk limits cannot be bypassed.

### Phase 4 — Paper trading and historical backtesting
**Status: Planned — first usable product milestone**
- [ ] Simulate availability checks, auction bids, acquisition fees, renewals, listings, offers, negotiations, and exits.
- [ ] Maintain a cash ledger and domain-level profit/loss ledger.
- [ ] Replay historical candidates without using future information in earlier decisions.
- [ ] Track prediction quality, simulated returns, drawdown, holding time, rejected opportunities, and data coverage.
- [ ] Provide a dashboard for decisions, portfolio, cash reserve, evidence, and run history.
- [ ] Add deterministic end-to-end scenarios and reproducible test fixtures.
**Exit criteria:** user can run a complete simulated cycle and inspect every decision without any external financial side effect.

### Phase 5 — Buyer discovery and sales workflow
**Status: Planned**
- [ ] Generate buyer profiles from relevant companies, products, markets, and use cases.
- [ ] Rank prospects by domain-to-business fit and record the evidence behind each match.
- [ ] Draft personalized outreach and follow-ups for review; do not send automatically in paper mode.
- [ ] Track contact status, replies, offers, negotiation history, opt-outs, and suppression lists.
- [ ] Add privacy-aware, compliant sending limits and deliverability checks before any live outreach.
**Exit criteria:** prospect lists and draft campaigns can be reviewed and audited; no email is sent without explicit live-mode authorization.

### Phase 6 — Learning and orchestration
**Status: Planned**
- [ ] Orchestrate discovery → enrichment → risk checks → paper decision → simulated acquisition → buyer research → simulated sale → evaluation.
- [ ] Compare predicted values and sale probabilities against verified outcomes.
- [ ] Track model versions, feature inputs, decision reasons, and experiment results.
- [ ] Use walk-forward/backtesting and holdout evaluation to avoid leakage and overfitting.
- [ ] Schedule jobs with retry/backoff, idempotency, monitoring, and a global pause control.
**Exit criteria:** learning updates are measurable, reproducible, reversible, and cannot weaken hard risk controls.

### Phase 7 — Controlled live integrations
**Status: Blocked until earlier exit criteria pass**
- [ ] Verify provider API availability, account permissions, fees, and terms.
- [ ] Implement provider adapters with dry-run support, idempotency, reconciliation, and failure recovery.
- [ ] Add explicit per-action approvals and configurable spending limits.
- [ ] Begin with read-only live data; then require separate approval for any live acquisition, paid listing, or outbound email capability.
- [ ] Test emergency stop and rollback/reconciliation procedures.
**Exit criteria:** security review, test suite, paper-trading evaluation, provider checks, and explicit user authorization are complete.

### Phase 8 — VPS deployment and operations
**Status: Planned**
- [ ] Document supported VPS sizing, environment variables, secrets, Docker deployment, migrations, and health checks.
- [ ] Configure HTTPS, backups, restore tests, monitoring, log rotation, and dependency updates.
- [ ] Add operational dashboard for job failures, data freshness, spending, and system health.
- [ ] Provide a deployment checklist and a safe upgrade/rollback procedure.
**Exit criteria:** repeatable deployment and restore test completed; live trading remains off by default.

## Initial architecture

1. **Discovery engine** — expired domains, registrar availability, auctions, marketplaces, trends, and name generation.
2. **Evidence/intelligence engine** — sales comparables, SEO/backlink quality, history, trend, trademark and spam screening, buyer demand.
3. **Decision/risk engine** — resale estimates, uncertainty, expected net return, bid ceiling, exposure and budget enforcement.
4. **Portfolio/acquisition engine** — paper acquisitions, auction simulations, cash ledger, renewal schedule, portfolio limits.
5. **Buyer/sales engine** — buyer research, contact matching, draft outreach, offers and negotiation tracking.
6. **Learning engine** — backtesting, prediction calibration, verified outcomes, model/version tracking.
7. **Orchestrator/operations** — scheduling, retries, audit logs, health checks, kill switch, and user-facing dashboard.

Reuse the existing FastAPI, PostgreSQL, Redis/Celery, and Next.js components where they prove reliable; refactor rather than adding services without a demonstrated need.

## Progress measurement

- **Project completion %** measures delivered, tested capabilities against the roadmap; it is not a promise of financial performance.
- **Audit completion %** is tracked separately from implementation progress.
- A phase is complete only when its exit criteria have evidence (tests, logs, reproducible steps, or verified behavior).
- Never mark a feature complete just because code exists.
- Update status.md whenever work is performed, with date, changed files, checks actually run, results, blockers, and next action.
