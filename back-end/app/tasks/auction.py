import logging
from app.celery_app import celery

logger = logging.getLogger(__name__)


@celery.task(name="app.tasks.auction.snipe", bind=True, max_retries=3)
def snipe(self, auction_id: int, max_bid: float):
    logger.info("Sniping auction %s up to $%.2f", auction_id, max_bid)
