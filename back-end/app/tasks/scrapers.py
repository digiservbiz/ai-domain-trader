import logging
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.celery_app import celery
from app.config import settings
from app.models.domain import Domain
from app.models.valuation import value as compute_value

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}
_EXPIRED_URL = (
    "https://www.expireddomains.net/domain-name-search/"
    "?fwhois=22&ftlds[]=2&ftlds[]=7"
)
_REDDIT_URL = "https://old.reddit.com/r/startups/new.json?limit=25"


def _db_session():
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    return sessionmaker(bind=engine)()


def _upsert(session, name: str, score: float, est_value: float):
    row = session.query(Domain).filter_by(name=name).first()
    if row:
        row.score = score
        row.est_value = est_value
    else:
        session.add(Domain(name=name, score=score, est_value=est_value))
    session.commit()


@celery.task(name="app.tasks.scrapers.scrape_expired_domains", bind=True, max_retries=3)
def scrape_expired_domains(self):
    """Fetch recently expired .com/.io domains and upsert valuations into DB."""
    try:
        resp = requests.get(_EXPIRED_URL, headers=_HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        names = []
        for row in soup.select("table.base1 tbody tr"):
            link = row.select_one("td.field_domain a")
            if link:
                name = link.get_text(strip=True).lower()
                if name and "." in name:
                    names.append(name)

        logger.info("Expired domains: found %d candidates", len(names))

        if not settings.DATABASE_URL:
            return {"scraped": 0, "reason": "no DATABASE_URL"}

        session = _db_session()
        saved = 0
        try:
            for name in names[:50]:
                try:
                    est = compute_value(name)
                    _upsert(session, name, score=round(est / 1000, 4), est_value=round(est, 2))
                    saved += 1
                except Exception as exc:
                    logger.warning("Skipping %s: %s", name, exc)
        finally:
            session.close()

        logger.info("Upserted %d domains", saved)
        return {"scraped": len(names), "saved": saved}

    except Exception as exc:
        logger.error("scrape_expired_domains failed: %s", exc)
        raise self.retry(exc=exc, countdown=60)


@celery.task(name="app.tasks.scrapers.scrape_reddit_trends", bind=True, max_retries=3)
def scrape_reddit_trends(self):
    """Pull trending startup titles from Reddit and log extracted keywords."""
    try:
        resp = requests.get(
            _REDDIT_URL,
            headers={**_HEADERS, "Accept": "application/json"},
            timeout=20,
        )
        resp.raise_for_status()
        posts = resp.json().get("data", {}).get("children", [])
        titles = [p["data"]["title"] for p in posts]

        # extract meaningful words as trend signals (used by name generation)
        keywords = []
        for title in titles[:15]:
            words = [w.strip(".,!?").lower() for w in title.split() if len(w) > 4]
            keywords.extend(words[:3])

        keywords = list(dict.fromkeys(keywords))[:30]  # dedupe, cap at 30
        logger.info("Reddit trends: %d keywords extracted", len(keywords))
        return {"titles": len(titles), "keywords": keywords}

    except Exception as exc:
        logger.error("scrape_reddit_trends failed: %s", exc)
        raise self.retry(exc=exc, countdown=60)
