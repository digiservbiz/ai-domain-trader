from celery import Celery
from celery.schedules import crontab
from app.config import settings

_broker = settings.REDIS_URL or "redis://redis:6379/0"

celery = Celery(
    "domain_trader",
    broker=_broker,
    backend=_broker,
    include=["app.tasks.scrapers", "app.tasks.auction"],
)

celery.conf.timezone = "UTC"
celery.conf.beat_schedule = {
    # scrape fresh expired domains every 6 hours
    "scrape-expired-domains": {
        "task": "app.tasks.scrapers.scrape_expired_domains",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    # pull Reddit startup trends every 3 hours
    "scrape-reddit-trends": {
        "task": "app.tasks.scrapers.scrape_reddit_trends",
        "schedule": crontab(minute=30, hour="*/3"),
    },
    "run-auction-sniper": {
        "task": "app.tasks.auction.run_sniper",
        "schedule": crontab(minute="*/30"),
    },
}
