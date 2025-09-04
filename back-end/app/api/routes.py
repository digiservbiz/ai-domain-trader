from fastapi import APIRouter
from app.services.namegen import brainstorm
from app.models.valuation import value

router = APIRouter()

@router.get("/generate")
def generate(niche: str, keywords: str):
    names = brainstorm(keywords.split(","), niche)
    return {"domains": names}

@router.get("/value/{domain}")
def get_value(domain: str):
    return {"domain": domain, "estValue": round(value(domain), 2)}
