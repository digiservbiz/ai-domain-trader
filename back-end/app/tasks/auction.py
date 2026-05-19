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
def snipe(self, domain: str, max_bid: float):
    if not settings.GODADDY_KEY or not settings.GODADDY_SECRET:
        logger.warning("GODADDY_KEY or GODADDY_SECRET not set; skipping snipe for %s", domain)
        return

    try:
        resp = requests.get(
            f"{_GODADDY_BASE}/v1/aftermarket/auctions/{domain}",
            headers=_auth_headers(),
            timeout=15,
        )

        session = _db_session()
        try:
            target = session.query(SnipeTarget).filter_by(domain=domain).first()

            if resp.status_code == 404 or resp.status_code != 200:
                if target:
                    target.status = "error"
                    target.last_checked = datetime.utcnow()
                    session.commit()
                return

            data = resp.json()
            current_bid = data.get("currentBid") or data.get("minimumNextBid", 0.0)

            if current_bid >= max_bid:
                if target:
                    target.status = "outbid"
                    target.current_bid = current_bid
                    target.last_checked = datetime.utcnow()
                    session.commit()
                return

            bid_resp = requests.post(
                f"{_GODADDY_BASE}/v1/aftermarket/auctions/{domain}/bids",
                headers={**_auth_headers(), "Content-Type": "application/json"},
                json={"amount": max_bid},
                timeout=15,
            )
            bid_resp.raise_for_status()

            if target:
                target.status = "bid_placed"
                target.current_bid = current_bid
                target.last_checked = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    except Exception as exc:
        logger.error("snipe failed for %s: %s", domain, exc)
        raise self.retry(exc=exc, countdown=120)


@celery.task(name="app.tasks.auction.run_sniper", bind=True, max_retries=3)
def run_sniper(self):
    try:
        session = _db_session()
        try:
            targets = (
                session.query(SnipeTarget)
                .filter(SnipeTarget.status.in_(["watching", "bid_placed"]))
                .all()
            )
            count = 0
            for target in targets:
                snipe.delay(target.domain, target.max_bid)
                count += 1
        finally:
            session.close()
        return {"triggered": count}
    except Exception as exc:
        logger.error("run_sniper failed: %s", exc)
        raise self.retry(exc=exc, countdown=120)
