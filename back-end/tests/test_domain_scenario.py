import pytest

from app.services.domain_scenario import run_paper_scenario


def test_scenario_replays_candidate_to_sale_and_reconciles_ledger():
    report = run_paper_scenario(
        domain="scenario.example.com",
        estimated_resale_value=500,
        sale_probability=0.8,
        acquisition_cost=50,
        additional_fees=5,
        annual_renewal_cost=15,
        holding_years=1,
        evidence_confidence=0.9,
        trademark_risk="low",
        realized_sale_price=500,
    )

    assert report["paper_trading_only"] is True
    assert report["real_world_actions"] is False
    assert [step["stage"] for step in report["lifecycle"]] == [
        "VALUATE", "PAPER_ACQUIRE", "PAPER_RENEW", "PAPER_SELL"
    ]
    assert report["reconciliation"] == {
        "starting_capital": 1000.0,
        "cash_balance": 1380.0,
        "open_positions": 0,
        "deployed_capital": 0,
        "realized_profit_loss": 380.0,
        "transaction_count": 3,
    }


def test_scenario_stops_without_acquiring_when_candidate_is_watch():
    report = run_paper_scenario(
        domain="uncertain.example.com",
        estimated_resale_value=100,
        sale_probability=0.1,
        acquisition_cost=30,
        evidence_confidence=0.2,
        trademark_risk="unknown",
    )

    assert report["decision"]["recommendation"] == "WATCH"
    assert [step["stage"] for step in report["lifecycle"]] == ["VALUATE", "STOP"]
    assert report["account"].positions == ()
    assert report["account"].transactions == ()


def test_scenario_rejects_invalid_holding_period_and_sale_price():
    with pytest.raises(ValueError, match="holding_years"):
        run_paper_scenario(
            domain="valid.com", estimated_resale_value=500, sale_probability=0.8,
            acquisition_cost=50, holding_years=-1,
        )
    with pytest.raises(ValueError, match="realized_sale_price"):
        run_paper_scenario(
            domain="valid.com", estimated_resale_value=500, sale_probability=0.8,
            acquisition_cost=50, realized_sale_price=0,
        )
