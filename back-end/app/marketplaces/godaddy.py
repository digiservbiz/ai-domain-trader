from .base import Marketplace
class GoDaddyMarketplace(Marketplace):
    def list(self, domain, price): return 'stub'
    def delist(self, id): return True
