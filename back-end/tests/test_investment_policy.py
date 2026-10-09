import pytest

from app.services.investment_policy import (
    InvestmentPolicy,
    Recommendation,
    evaluate_candidate,
)


def test_good_candidate_is_only_a_paper_candidate():
    result = evaluate_candidate(
        domain="  Brandable.com. ",
        estimated_resale_value=500,
        sale_probability=0.8,
        acquisition_cost=50,
        additional_fees=5,
        annual_renewal_cost=15,
        holding_years=1,
        evidence_confidence=0.9,
        trademark_risk="low",
    )

    assert result["domain"] == "brandable.com"
    assert result["recommendation"] == Recommendation.BUY_CANDIDATE.value
    assert result["paper_trading_only"] is True
    assert result["purchase_executed"] is False
    assert result["financials"]["all_in_acquisition_cost"] == 55
    assert result["financials"]["expected_net_profit"] == 290


def test_high_trademark_risk_is_rejected():
    result = evaluate_candidate(
        domain="brand.com",
        estimated_resale_value=1000,
        sale_probability=0.9,
        acquisition_cost=20,
        evidence_confidence=0.95,
        trademark_risk="high",
    )

    assert result["recommendation"] == Recommendation.REJECT.value
    assert any("trademark risk" in reason.lower() for reason in result["reasons"])


def test_per_domain_and_portfolio_limits_are_hard_rejections():
    policy = InvestmentPolicy(max_domain_cost=100, max_deployed_capital=500)
    over_domain_limit = evaluate_candidate(
        domain="costly.com",
        estimated_resale_value=1000,
        sale_probability=0.9,
        acquisition_cost=101,
        evidence_confidence=0.9,
        trademark_risk="low",
        policy=policy,
    )
    over_portfolio_limit = evaluate_candidate(
        domain="next.com",
        estimated_resale_value=1000,
        sale_probability=0.9,
        acquisition_cost=60,
        current_deployed_capital=450,
        evidence_confidence=0.9,
        trademark_risk="low",
        policy=policy,
    )

    assert over_domain_limit["recommendation"] == Recommendation.REJECT.value
    assert over_portfolio_limit["recommendation"] == Recommendation.REJECT.value


def test_low_confidence_or_unknown_trademark_risk_never_gets_buy_candidate():
    result = evaluate_candidate(
        domain="uncertain.com",
        estimated_resale_value=1000,
        sale_probability=0.9,
        acquisition_cost=20,
        evidence_confidence=0.4,
        trademark_risk="unknown",
    )

    assert result["recommendation"] == Recommendation.WATCH.value


@pytest.mark.parametrize(
    "kwargs",
    [
        {"sale_probability": 1.2},
        {"evidence_confidence": -0.1},
        {"acquisition_cost": -1},
        {"estimated_resale_value": float("inf")},
    ],
)
def test_invalid_candidate_inputs_are_rejected(kwargs):
    values = {
        "domain": "valid.com",
        "estimated_resale_value": 500,
        "sale_probability": 0.7,
        "acquisition_cost": 20,
        "evidence_confidence": 0.8,
        "trademark_risk": "low",
    }
    values.update(kwargs)

    with pytest.raises(ValueError):
        evaluate_candidate(**values)


def test_maximum_bid_respects_domain_cap_and_additional_fees():
    result = evaluate_candidate(
        domain="bid.com",
        estimated_resale_value=500,
        sale_probability=0.8,
        acquisition_cost=20,
        additional_fees=10,
        evidence_confidence=0.8,
        trademark_risk="low",
    )

    assert result["financials"]["maximum_permitted_bid"] == 90
