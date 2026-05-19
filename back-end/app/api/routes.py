from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.namegen import brainstorm
from app.models.valuation import value
from app.marketplaces.godaddy import GoDaddyMarketplace
from app.core.security import get_current_user
from app.db.base import get_db
from app.models.domain import Domain

router = APIRouter()


@router.get("/domains")
def search_domains(
    q: Optional[str] = None,
    tld: Optional[str] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    limit = min(limit, 100)
    query = db.query(Domain)
    if q is not None:
        query = query.filter(Domain.name.ilike(f"%{q}%"))
    if tld is not None:
        query = query.filter(Domain.name.ilike(f"%.{tld}"))
    if min_score is not None:
        query = query.filter(Domain.score >= min_score)
    if max_score is not None:
        query = query.filter(Domain.score <= max_score)
    if min_value is not None:
        query = query.filter(Domain.est_value >= min_value)
    if max_value is not None:
        query = query.filter(Domain.est_value <= max_value)
    query = query.order_by(Domain.score.desc())
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    pages = max(1, -(-total // limit))
    return {
        "items": [{"domain": d.name, "score": round(d.score, 1), "estValue": round(d.est_value, 2)} for d in items],
        "total": total,
        "page": page,
        "pages": pages,
    }


@router.get("/generate")
def generate(niche: str, keywords: str):
    names = brainstorm(keywords.split(","), niche)
    return {"domains": names}


@router.get("/value/{domain}")
def get_value(domain: str):
    return {"domain": domain, "estValue": round(value(domain), 2)}


@router.get("/domains/{domain}/check")
def check_domain(domain: str):
    return GoDaddyMarketplace().check_availability(domain)


class ListBody(BaseModel):
    price: float


@router.post("/domains/{domain}/list")
def list_domain(domain: str, body: ListBody, _: dict = Depends(get_current_user)):
    GoDaddyMarketplace().list(domain, body.price)
    return {"listed": True, "domain": domain, "price": body.price}


@router.delete("/domains/{domain}/list")
def delist_domain(domain: str, _: dict = Depends(get_current_user)):
    GoDaddyMarketplace().delist(domain)
    return {"delisted": True, "domain": domain}
