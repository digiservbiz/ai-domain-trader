"""Deterministic, conservative investment guardrails for domain candidates.

This module deliberately has no network, database, or payment side effects. It
can be used by API handlers, Celery jobs, and tests without invoking an AI model.
"""
from dataclasses import asdict, dataclass
from enum import Enum
from math import isfinite


class Recommendation(str, Enum):
    BUY_CANDIDATE = "BUY_CANDIDATE"
    WATCH = "WATCH"
    REJECT = "REJECT"


@dataclass(frozen=True)
class InvestmentPolicy:
    """Hard limits for paper trading; monetary values use one currency (EUR by default)."""

    starting_capital: float = 1000.0
    max_domain_cost: float = 100.0
    max_deployed_capital: float = 500.0
    reserve_capital: float = 500.0
    minimum_expected_profit: float = 50.0
    minimum_expected_roi: float = 0.30
    marketplace_fee_rate: float = 0.10
    default_holding_years: int = 2

    def validate(self) -> None:
        numeric_values = (
            self.starting_capital,
            self.max_domain_cost,
            self.max_deployed_capital,
            self.reserve_capital,
            self.minimum_expected_profit,
            self.minimum_expected_roi,
            self.marketplace_fee_rate,
        )
        if not all(isfinite(value) and value >= 0 for value in numeric_values):
            raise ValueError("Policy values must be finite and non-negative")
        if self.marketplace_fee_rate >= 1:
            raise ValueError("marketplace_fee_rate must be less than 1")
        if self.max_domain_cost > self.starting_capital:
            raise ValueError("max_domain_cost cannot exceed starting_capital")
        if self.max_deployed_capital > self.starting_capital:
            raise ValueError("max_deployed_capital cannot exceed starting_capital")
        if self.reserve_capital > self.starting_capital:
            raise ValueError("reserve_capital cannot exceed starting_capital")
        if self.max_deployed_capital + self.reserve_capital > self.starting_capital:
            raise ValueError("max_deployed_capital plus reserve_capital cannot exceed starting_capital")
        if self.default_holding_years < 0:
            raise ValueError("default_holding_years must be non-negative")


DEFAULT_POLICY = InvestmentPolicy()


def evaluate_candidate(
    *,
    domain: str,
    estimated_resale_value: float,
    sale_probability: float,
    acquisition_cost: float,
    additional_fees: float = 0.0,
    annual_renewal_cost: float = 15.0,
    holding_years: int | None = None,
    current_deployed_capital: float = 0.0,
    evidence_confidence: float = 0.5,
    trademark_risk: str = "unknown",
    policy: InvestmentPolicy = DEFAULT_POLICY,
) -> dict:
    """Return an explainable candidate decision; never executes a purchase or bid."""
    policy.validate()
    normalized_domain = domain.strip().lower().rstrip(".")
    if not normalized_domain or "." not in normalized_domain:
        raise ValueError("domain must be a fully qualified domain name")

    numbers = {
        "estimated_resale_value": estimated_resale_value,
        "sale_probability": sale_probability,
        "acquisition_cost": acquisition_cost,
        "additional_fees": additional_fees,
        "annual_renewal_cost": annual_renewal_cost,
        "current_deployed_capital": current_deployed_capital,
        "evidence_confidence": evidence_confidence,
    }
    if not all(isfinite(value) for value in numbers.values()):
        raise ValueError("Candidate inputs must be finite numbers")
    if estimated_resale_value < 0 or acquisition_cost < 0 or additional_fees < 0:
        raise ValueError("Values and costs must be non-negative")
    if annual_renewal_cost < 0 or current_deployed_capital < 0:
        raise ValueError("Renewal and deployed capital must be non-negative")
    if not 0 <= sale_probability <= 1:
        raise ValueError("sale_probability must be between 0 and 1")
    if not 0 <= evidence_confidence <= 1:
        raise ValueError("evidence_confidence must be between 0 and 1")
    if trademark_risk not in {"low", "medium", "high", "unknown"}:
        raise ValueError("trademark_risk must be low, medium, high, or unknown")

    years = policy.default_holding_years if holding_years is None else holding_years
    if years < 0:
        raise ValueError("holding_years must be non-negative")

    all_in_cost = acquisition_cost + additional_fees
    renewals = annual_renewal_cost * years
    expected_sale_proceeds = estimated_resale_value * sale_probability
    expected_marketplace_fees = expected_sale_proceeds * policy.marketplace_fee_rate
    expected_net_profit = (
        expected_sale_proceeds - expected_marketplace_fees - all_in_cost - renewals
    )
    total_expected_cost = all_in_cost + renewals
    expected_roi = (
        expected_net_profit / total_expected_cost if total_expected_cost > 0 else 0.0
    )
    spendable_capital = policy.starting_capital - policy.reserve_capital
    budget_remaining = max(
        0.0,
        min(
            spendable_capital - current_deployed_capital,
            policy.max_deployed_capital - current_deployed_capital,
        ),
    )
    max_bid_by_domain_cap = max(0.0, policy.max_domain_cost - additional_fees)
    max_bid = min(max_bid_by_domain_cap, budget_remaining - additional_fees)
    max_bid = max(0.0, max_bid)

    reasons = []
    hard_reject = False
    if trademark_risk == "high":
        reasons.append("High trademark risk: reject pending specialist clearance.")
        hard_reject = True
    if all_in_cost > policy.max_domain_cost:
        reasons.append("All-in acquisition cost exceeds the per-domain limit.")
        hard_reject = True
    if current_deployed_capital + all_in_cost > policy.max_deployed_capital:
        reasons.append("Acquisition would exceed the portfolio exposure limit.")
        hard_reject = True
    if all_in_cost > budget_remaining:
        reasons.append("Insufficient uncommitted capital for this acquisition.")
        hard_reject = True
    if evidence_confidence < 0.5:
        reasons.append("Evidence confidence is low; verify data before investing.")
    if trademark_risk == "unknown":
        reasons.append("Trademark risk has not been assessed.")
    if expected_net_profit < policy.minimum_expected_profit:
        reasons.append("Expected net profit is below the policy minimum.")
    if expected_roi < policy.minimum_expected_roi:
        reasons.append("Expected ROI is below the policy minimum.")

    if hard_reject:
        recommendation = Recommendation.REJECT
    elif (
        evidence_confidence >= 0.7
        and trademark_risk == "low"
        and expected_net_profit >= policy.minimum_expected_profit
        and expected_roi >= policy.minimum_expected_roi
    ):
        recommendation = Recommendation.BUY_CANDIDATE
        reasons.append("Candidate meets the configured paper-trading policy; this is not a purchase.")
    else:
        recommendation = Recommendation.WATCH
        if not reasons:
            reasons.append("More evidence is required before a decision.")

    return {
        "domain": normalized_domain,
        "recommendation": recommendation.value,
        "currency": "EUR",
        "paper_trading_only": True,
        "purchase_executed": False,
        "inputs": {
            "estimated_resale_value": round(estimated_resale_value, 2),
            "sale_probability": round(sale_probability, 4),
            "acquisition_cost": round(acquisition_cost, 2),
            "additional_fees": round(additional_fees, 2),
            "annual_renewal_cost": round(annual_renewal_cost, 2),
            "holding_years": years,
            "evidence_confidence": round(evidence_confidence, 4),
            "trademark_risk": trademark_risk,
        },
        "financials": {
            "all_in_acquisition_cost": round(all_in_cost, 2),
            "estimated_renewals": round(renewals, 2),
            "expected_sale_proceeds_before_fees": round(expected_sale_proceeds, 2),
            "expected_marketplace_fees": round(expected_marketplace_fees, 2),
            "expected_net_profit": round(expected_net_profit, 2),
            "expected_roi": round(expected_roi, 4),
            "current_deployed_capital": round(current_deployed_capital, 2),
            "budget_remaining_before_acquisition": round(budget_remaining, 2),
            "maximum_permitted_bid": round(max_bid, 2),
        },
        "policy": asdict(policy),
        "reasons": reasons,
    }
