import scrapy
class ExpiredSpider(scrapy.Spider):
    name = 'expired'
    start_urls = ['https://www.expireddomains.net']
    def parse(self, response):
        for row in response.css('table.base1 tbody tr'):
            yield {'domain': row.css('td a::text').get()}
