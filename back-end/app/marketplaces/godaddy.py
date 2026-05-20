import os
import requests
from fastapi import HTTPException
from app.config import settings
from .base import Marketplace


class GoDaddyMarketplace(Marketplace):
    def __init__(self):
        if not settings.GODADDY_KEY or not settings.GODADDY_SECRET:
            raise HTTPException(503, "GoDaddy credentials not configured")
        sandbox = os.getenv("GODADDY_SANDBOX", "false").lower() == "true"
        self.base_url = "https://api.ote-godaddy.com" if sandbox else "https://api.godaddy.com"
        self.headers = {
            "Authorization": f"sso-key {settings.GODADDY_KEY}:{settings.GODADDY_SECRET}",
            "Content-Type": "application/json",
        }

    def check_availability(self, domain: str) -> dict:
        try:
            resp = requests.get(
                f"{self.base_url}/v1/domains/available",
                params={"domain": domain},
                headers=self.headers,
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            return {
                "domain": domain,
                "available": bool(data.get("available", False)),
                "price": float(data.get("price", 0)) / 1_000_000,
                "currency": data.get("currency", "USD"),
            }
        except Exception:
            return {"available": False}

    def list(self, domain: str, price: float) -> str:
        payload = [{"domain": domain, "price": int(price * 1_000_000), "currency": "USD", "listingType": "AUCTION"}]
        resp = requests.post(
            f"{self.base_url}/v1/aftermarket/listings",
            json=payload,
            headers=self.headers,
            timeout=10,
        )
        if not resp.ok:
            raise HTTPException(502, f"GoDaddy listing failed: {resp.text}")
        return domain

    def delist(self, domain: str) -> bool:
        resp = requests.delete(
            f"{self.base_url}/v1/aftermarket/listings/{domain}",
            headers=self.headers,
            timeout=10,
        )
        if resp.status_code == 404:
            return False
        if not resp.ok:
            raise HTTPException(502, f"GoDaddy delist failed: {resp.text}")
        return True
