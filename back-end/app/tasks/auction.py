import logging
from datetime import datetime

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.celery_app import celery
from app.config import settings
from app.models.snipe_target import SnipeTarget

logger = logging.getLogger(__name__)

_GODADDY_BASE = "https://api.godaddy.com"


def _db_session():
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    return sessionmaker(bind=engine)()


def _auth_headers():
    return {"Authorization": f"sso-key {settings.GODADDY_KEY}:{settings.GODADDY_SECRET}"}


@celery.task(name="app.tasks.auction.snipe", bind=True, max_retries=3)
def snipe(self, target_id: int):
    # Fail closed before any database/network work in the default paper-trading mode.
    if not settings.can_place_live_bids:
        logger.warning("Live bidding disabled; paper mode skipped target %s", target_id)
        return {"skipped": True, "mode": "paper", "reason": "live bidding disabled"}
    if not settings.GODADDY_KEY or not settings.GODADDY_SECRET:
        logger.warning("GoDaddy credentials missing; skipping target %s", target_id)
        return {"skipped": True, "mode": "live", "reason": "GoDaddy credentials missing"}

    session = _db_session()
    try:
        # Use the immutable primary key, never a domain-only lookup: different users
        # may legitimately watch the same domain and must not update each other's row.
        target = session.query(SnipeTarget).filter(SnipeTarget.id == target_id).first()
        if not target:
            return {"skipped": True, "mode": "live", "reason": "watch target no longer exists"}
        domain = target.domain
        max_bid = target.max_bid

        resp = requests.get(
            f"{_GODADDY_BASE}/v1/aftermarket/auctions/{domain}",
            headers=_auth_headers(),
            timeout=15,
        )

        if resp.status_code != 200:
            target.status = "error"
            target.last_checked = datetime.utcnow()
            session.commit()
            return {"skipped": True, "reason": f"auction lookup status {resp.status_code}"}

        data = resp.json()
        current_bid = data.get("currentBid") or data.get("minimumNextBid", 0.0)

        if current_bid >= max_bid:
            target.status = "outbid"
            target.current_bid = current_bid
            target.last_checked = datetime.utcnow()
            session.commit()
            return {"skipped": True, "reason": "current bid reached configured maximum"}

        bid_resp = requests.post(
            f"{_GODADDY_BASE}/v1/aftermarket/auctions/{domain}/bids",
            headers={**_auth_headers(), "Content-Type": "application/json"},
            json={"amount": max_bid},
            timeout=15,
        )
        bid_resp.raise_for_status()

        target.status = "bid_placed"
        target.current_bid = current_bid
        target.last_checked = datetime.utcnow()
        session.commit()
        return {"skipped": False, "mode": "live", "domain": domain, "bid": max_bid}
    except Exception as exc:
        session.rollback()
        logger.error("snipe target %s failed: %s", target_id, exc)
        raise self.retry(exc=exc, countdown=120)
    finally:
        session.close()


@celery.task(name="app.tasks.auction.run_sniper", bind=True, max_retries=3)
def run_sniper(self):
    if not settings.can_place_live_bids:
        logger.warning("Live sniper scheduler disabled in paper mode")
        return {"triggered": 0, "mode": "paper", "reason": "live bidding disabled"}
    try:
        session = _db_session()
        try:
            targets = (
                session.query(SnipeTarget)
                .filter(SnipeTarget.status.in_(["watching", "bid_placed"]))
                .all()
            )
            target_ids = [target.id for target in targets]
        finally:
            session.close()

        for target_id in target_ids:
            snipe.delay(target_id)
        return {"triggered": len(target_ids), "mode": "live"}
    except Exception as exc:
        logger.error("run_sniper failed: %s", exc)
        raise self.retry(exc=exc, countdown=120)
