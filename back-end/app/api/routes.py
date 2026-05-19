from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.namegen import brainstorm
from app.models.valuation import value
from app.marketplaces.godaddy import GoDaddyMarketplace
from app.core.security import get_current_user

router = APIRouter()


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
