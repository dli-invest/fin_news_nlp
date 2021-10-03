import scrapy
from scrapy.crawler import CrawlerProcess
import urllib

settings = {}


class ScraperWithDuplicateRequests(scrapy.Spider):
    name = "ScraperWithDuplicateRequests"
    start_urls = [
        "https://friendlyuser.github.io",
        "https://david-li.me",
        "https://investing.david-li.me",
        "http://tex-diagrams.david-li.me",
        "https://dli-invest.github.io"
    ]

    custom_settings = {"DEPTH_LIMIT": 2}

    allowed_domains = [
        "https://friendlyuser.github.io",
        "https://david-li.me",
        "https://investing.david-li.me",
        "https://dli-invest.github.io",
        "http://tex-diagrams.david-li.me",
        "https://tex-diagrams.david-li.me",
    ]

    def parse(self, response):
        for next_page in response.css("a::attr(href)").extract():
            if next_page is not None:
                # ignore mailto and tel links
                if next_page[0:3] == "tel":
                    continue
                elif next_page[0:6] == "mailto":
                    continue
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)

        for quote in response.css("p"):
            yield {"quote": quote.extract()}