"""Deterministic end-to-end paper scenario; never performs external side effects."""
from app.services.investment_policy import InvestmentPolicy, evaluate_candidate
from app.services.paper_trading import PaperAccount, acquire, new_account, renew, sell


def run_paper_scenario(
    *,
    domain: str,
    estimated_resale_value: float,
    sale_probability: float,
    acquisition_cost: float,
    additional_fees: float = 0.0,
    annual_renewal_cost: float = 15.0,
    holding_years: int = 2,
    evidence_confidence: float = 0.5,
    trademark_risk: str = "unknown",
    realized_sale_price: float | None = None,
    policy: InvestmentPolicy = InvestmentPolicy(),
) -> dict:
    """Evaluate, simulate acquisition/renewals, and optionally simulate a sale.

    A candidate that is not BUY_CANDIDATE is never acquired. A sale price is an
    explicit scenario input, not a forecast. All operations use the pure paper
    ledger, and the returned report states that no real-world action occurred.
    """
    if holding_years < 0:
        raise ValueError("holding_years must be non-negative")
    if realized_sale_price is not None and realized_sale_price <= 0:
        raise ValueError("realized_sale_price must be positive when supplied")

    decision = evaluate_candidate(
        domain=domain,
        estimated_resale_value=estimated_resale_value,
        sale_probability=sale_probability,
        acquisition_cost=acquisition_cost,
        additional_fees=additional_fees,
        annual_renewal_cost=annual_renewal_cost,
        holding_years=holding_years,
        evidence_confidence=evidence_confidence,
        trademark_risk=trademark_risk,
        policy=policy,
    )
    account: PaperAccount = new_account(policy)
    lifecycle = [{"stage": "VALUATE", "result": decision["recommendation"]}]

    if decision["recommendation"] != "BUY_CANDIDATE":
        lifecycle.append({"stage": "STOP", "reason": "Candidate did not meet buy-candidate policy"})
        return {
            "domain": decision["domain"],
            "paper_trading_only": True,
            "real_world_actions": False,
            "decision": decision,
            "lifecycle": lifecycle,
            "account": account,
        }

    account = acquire(
        account,
        domain=domain,
        acquisition_cost=acquisition_cost,
        additional_fees=additional_fees,
        annual_renewal_cost=annual_renewal_cost,
    )
    lifecycle.append({"stage": "PAPER_ACQUIRE", "amount": round(acquisition_cost + additional_fees, 2)})

    for year in range(holding_years):
        account = renew(account, domain=domain)
        lifecycle.append({"stage": "PAPER_RENEW", "year": year + 1, "amount": round(annual_renewal_cost, 2)})

    if realized_sale_price is not None:
        account = sell(account, domain=domain, gross_sale_price=realized_sale_price)
        lifecycle.append({
            "stage": "PAPER_SELL",
            "gross_sale_price": round(realized_sale_price, 2),
            "realized_profit_loss": account.realized_profit,
        })
    else:
        lifecycle.append({"stage": "HOLD", "reason": "No explicit simulated sale price supplied"})

    return {
        "domain": decision["domain"],
        "paper_trading_only": True,
        "real_world_actions": False,
        "decision": decision,
        "lifecycle": lifecycle,
        "account": account,
        "reconciliation": {
            "starting_capital": account.starting_capital,
            "cash_balance": account.cash_balance,
            "open_positions": len(account.positions),
            "deployed_capital": account.deployed_capital,
            "realized_profit_loss": account.realized_profit,
            "transaction_count": len(account.transactions),
        },
    }
