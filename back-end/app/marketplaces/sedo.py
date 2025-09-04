from .base import Marketplace
class SedoMarketplace(Marketplace):
    def list(self, domain, price): return 'stub'
    def delist(self, id): return True
