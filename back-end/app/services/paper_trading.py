"""Deterministic paper-trading ledger.

This module is intentionally isolated from marketplace, email, payment, and database
integrations. Every operation returns a new immutable account and records a simulated
transaction; it cannot place bids, purchase domains, or contact buyers.
"""
from dataclasses import dataclass
from math import isfinite

from app.services.investment_policy import InvestmentPolicy


@dataclass(frozen=True)
class PaperPosition:
    domain: str
    acquisition_cost: float
    carrying_cost: float
    annual_renewal_cost: float


@dataclass(frozen=True)
class PaperTransaction:
    action: str
    domain: str
    amount: float
    detail: str


@dataclass(frozen=True)
class PaperAccount:
    starting_capital: float = 1000.0
    cash_balance: float = 1000.0
    reserve_capital: float = 500.0
    max_domain_cost: float = 100.0
    max_deployed_capital: float = 500.0
    marketplace_fee_rate: float = 0.10
    positions: tuple[PaperPosition, ...] = ()
    transactions: tuple[PaperTransaction, ...] = ()
    realized_profit: float = 0.0

    @property
    def deployed_capital(self) -> float:
        """Total carrying cost at risk, including renewals already paid."""
        return round(sum(position.carrying_cost for position in self.positions), 2)

    @property
    def paper_trading_only(self) -> bool:
        return True


def new_account(policy: InvestmentPolicy = InvestmentPolicy()) -> PaperAccount:
    """Create an empty paper account from the validated investment policy."""
    policy.validate()
    return PaperAccount(
        starting_capital=policy.starting_capital,
        cash_balance=policy.starting_capital,
        reserve_capital=policy.reserve_capital,
        max_domain_cost=policy.max_domain_cost,
        max_deployed_capital=policy.max_deployed_capital,
        marketplace_fee_rate=policy.marketplace_fee_rate,
    )


def acquire(
    account: PaperAccount,
    *,
    domain: str,
    acquisition_cost: float,
    additional_fees: float = 0.0,
    annual_renewal_cost: float = 15.0,
) -> PaperAccount:
    """Simulate acquisition only; enforce all-in domain, exposure, and reserve caps."""
    normalized_domain = domain.strip().lower().rstrip(".")
    if not normalized_domain or "." not in normalized_domain:
        raise ValueError("domain must be a fully qualified domain name")
    amounts = (acquisition_cost, additional_fees, annual_renewal_cost)
    if not all(isfinite(amount) and amount >= 0 for amount in amounts):
        raise ValueError("Costs must be finite and non-negative")
    if acquisition_cost + additional_fees <= 0:
        raise ValueError("All-in acquisition cost must be greater than zero")
    if any(position.domain == normalized_domain for position in account.positions):
        raise ValueError("Domain already exists in the paper portfolio")

    all_in_cost = round(acquisition_cost + additional_fees, 2)
    spendable_cash = account.cash_balance - account.reserve_capital
    if all_in_cost > account.max_domain_cost:
        raise ValueError("All-in cost exceeds the per-domain limit")
    if account.deployed_capital + all_in_cost > account.max_deployed_capital:
        raise ValueError("Acquisition exceeds the portfolio exposure limit")
    if all_in_cost > spendable_cash:
        raise ValueError("Acquisition would consume reserved capital")

    position = PaperPosition(
        domain=normalized_domain,
        acquisition_cost=all_in_cost,
        carrying_cost=all_in_cost,
        annual_renewal_cost=annual_renewal_cost,
    )
    transaction = PaperTransaction(
        action="ACQUIRE",
        domain=normalized_domain,
        amount=all_in_cost,
        detail="Simulated acquisition; no real purchase or bid was placed.",
    )
    return PaperAccount(
        **{
            **account.__dict__,
            "cash_balance": round(account.cash_balance - all_in_cost, 2),
            "positions": account.positions + (position,),
            "transactions": account.transactions + (transaction,),
        }
    )


def renew(account: PaperAccount, *, domain: str) -> PaperAccount:
    """Simulate one annual renewal and include it in carrying cost and exposure."""
    normalized_domain = domain.strip().lower().rstrip(".")
    position = next((p for p in account.positions if p.domain == normalized_domain), None)
    if position is None:
        raise ValueError("Domain is not held in the paper portfolio")
    cost = position.annual_renewal_cost
    if account.deployed_capital + cost > account.max_deployed_capital:
        raise ValueError("Renewal would exceed the portfolio exposure limit")
    if cost > account.cash_balance - account.reserve_capital:
        raise ValueError("Renewal would consume reserved capital")

    renewed = PaperPosition(
        domain=position.domain,
        acquisition_cost=position.acquisition_cost,
        carrying_cost=round(position.carrying_cost + cost, 2),
        annual_renewal_cost=position.annual_renewal_cost,
    )
    positions = tuple(renewed if p.domain == normalized_domain else p for p in account.positions)
    transaction = PaperTransaction(
        action="RENEW",
        domain=normalized_domain,
        amount=cost,
        detail="Simulated annual renewal; no registrar charge was made.",
    )
    return PaperAccount(
        **{
            **account.__dict__,
            "cash_balance": round(account.cash_balance - cost, 2),
            "positions": positions,
            "transactions": account.transactions + (transaction,),
        }
    )


def sell(account: PaperAccount, *, domain: str, gross_sale_price: float) -> PaperAccount:
    """Simulate a sale, subtract marketplace fees, and realize net profit or loss."""
    normalized_domain = domain.strip().lower().rstrip(".")
    if not isfinite(gross_sale_price) or gross_sale_price <= 0:
        raise ValueError("gross_sale_price must be a finite positive number")
    position = next((p for p in account.positions if p.domain == normalized_domain), None)
    if position is None:
        raise ValueError("Domain is not held in the paper portfolio")

    fees = round(gross_sale_price * account.marketplace_fee_rate, 2)
    net_proceeds = round(gross_sale_price - fees, 2)
    profit = round(net_proceeds - position.carrying_cost, 2)
    transaction = PaperTransaction(
        action="SELL",
        domain=normalized_domain,
        amount=net_proceeds,
        detail=(
            f"Simulated sale at {gross_sale_price:.2f}; marketplace fees {fees:.2f}; "
            f"realized profit/loss {profit:.2f}. No real sale was made."
        ),
    )
    return PaperAccount(
        **{
            **account.__dict__,
            "cash_balance": round(account.cash_balance + net_proceeds, 2),
            "positions": tuple(p for p in account.positions if p.domain != normalized_domain),
            "transactions": account.transactions + (transaction,),
            "realized_profit": round(account.realized_profit + profit, 2),
        }
    )
