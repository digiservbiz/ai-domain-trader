import pytest

from app.services.paper_trading import acquire, new_account, renew, sell


def test_paper_round_trip_reconciles_cash_costs_fees_and_profit():
    account = new_account()
    account = acquire(
        account,
        domain="Brandable.com.",
        acquisition_cost=50,
        additional_fees=5,
        annual_renewal_cost=15,
    )
    assert account.cash_balance == 945
    assert account.deployed_capital == 55
    assert account.paper_trading_only is True
    assert account.transactions[-1].action == "ACQUIRE"

    account = renew(account, domain="brandable.com")
    assert account.cash_balance == 930
    assert account.positions[0].carrying_cost == 70

    account = sell(account, domain="brandable.com", gross_sale_price=500)
    assert account.cash_balance == 1380
    assert account.realized_profit == 380
    assert account.positions == ()
    assert [tx.action for tx in account.transactions] == ["ACQUIRE", "RENEW", "SELL"]
    assert "No real sale was made" in account.transactions[-1].detail


def test_paper_acquisition_enforces_domain_cap_and_reserve():
    account = new_account()
    with pytest.raises(ValueError, match="per-domain"):
        acquire(account, domain="too-expensive.com", acquisition_cost=99, additional_fees=2)

    constrained = new_account()
    from dataclasses import replace

    constrained = replace(constrained, cash_balance=510)
    with pytest.raises(ValueError, match="reserved capital"):
        acquire(constrained, domain="reserve.com", acquisition_cost=20)


def test_paper_ledger_rejects_duplicate_domains_and_unknown_sale():
    account = acquire(new_account(), domain="owned.com", acquisition_cost=25)
    with pytest.raises(ValueError, match="already exists"):
        acquire(account, domain="OWNED.com", acquisition_cost=20)
    with pytest.raises(ValueError, match="not held"):
        sell(account, domain="unknown.com", gross_sale_price=100)


def test_paper_ledger_rejects_invalid_amounts():
    with pytest.raises(ValueError, match="finite and non-negative"):
        acquire(new_account(), domain="bad.com", acquisition_cost=float("nan"))
    with pytest.raises(ValueError, match="positive"):
        sell(new_account(), domain="not-held.com", gross_sale_price=0)
