import scrapy
class TikTokSpider(scrapy.Spider):
    name = 'tiktok'
    start_urls = ['https://trenddiscovery.com/tiktok']
    def parse(self, response):
        for tag in response.css('.tag'):
            yield {'tag': tag.css('::text').get()}
