from celery import shared_task
@shared_task(bind=True, max_retries=3)
def snipe(self, auction_id: int, max_bid: float):
    print(f'Sniping auction {auction_id} up to ')
