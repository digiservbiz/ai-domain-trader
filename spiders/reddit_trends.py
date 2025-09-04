import scrapy
class RedditSpider(scrapy.Spider):
    name = 'reddit'
    start_urls = ['https://old.reddit.com/r/startups/new/']
    def parse(self, response):
        for post in response.css('a.title'):
            yield {'title': post.css('::text').get()}
