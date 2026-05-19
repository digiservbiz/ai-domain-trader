from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.base import get_db
from app.core.security import get_current_user
from app.models.portfolio import PortfolioItem
from app.models.valuation import value

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class PortfolioItemCreate(BaseModel):
    domain: str
    bought_price: float


def _item_dict(item: PortfolioItem) -> dict:
    current_value = value(item.domain)
    pnl = current_value - item.bought_price
    pnl_pct = (pnl / item.bought_price * 100) if item.bought_price else 0.0
    return {
        "domain": item.domain,
        "bought_price": item.bought_price,
        "bought_at": item.bought_at.isoformat(),
        "current_value": current_value,
        "pnl": pnl,
        "pnl_pct": pnl_pct,
    }


@router.get("")
def get_portfolio(
    db: Session = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    items = db.query(PortfolioItem).all()
    item_dicts = [_item_dict(item) for item in items]
    total_invested = sum(d["bought_price"] for d in item_dicts)
    total_current = sum(d["current_value"] for d in item_dicts)
    return {
        "items": item_dicts,
        "total_invested": total_invested,
        "total_current": total_current,
        "total_pnl": total_current - total_invested,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def add_portfolio_item(
    body: PortfolioItemCreate,
    db: Session = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    existing = db.query(PortfolioItem).filter(PortfolioItem.domain == body.domain).first()
    if existing:
        raise HTTPException(status_code=400, detail="Domain already in portfolio")
    item = PortfolioItem(domain=body.domain, bought_price=body.bought_price)
    db.add(item)
    db.commit()
    db.refresh(item)
    return _item_dict(item)


@router.delete("/{domain}")
def delete_portfolio_item(
    domain: str,
    db: Session = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    item = db.query(PortfolioItem).filter(PortfolioItem.domain == domain).first()
    if not item:
        raise HTTPException(status_code=404, detail="Domain not found in portfolio")
    db.delete(item)
    db.commit()
    return {"deleted": True, "domain": domain}
