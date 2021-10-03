import scrapy
from scrapy.crawler import CrawlerProcess
import sys
import os.path
# # Import from sibling directory ..\api
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../nlp_api")
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../nlp_api/app")

from nlp_api.app.nlp import nlp, init_nlp
init_nlp("assets/data/exchanges.tsv","assets/data/indicies.tsv")
settings = {}

print(nlp)
class ScraperForSeekingAlpha(scrapy.Spider):
    name = "ScraperWithDuplicateRequests"
    start_urls = [
        "https://seekingalpha.com/market-news"
    ]

    custom_settings = {"DEPTH_LIMIT": 2}

    allowed_domains = [
        "https://seekingalpha.com/"
    ]

    def parse(self, response):
        for link_tag in response.xpath('//a'):
            sasource = link_tag.xpath('./sasource').get()
            if sasource not in ["market_news_all_1", "market_news_headlines_1"]:
                continue
            href= link_tag.xpath('./@href').get()
            print(link_tag)
            if href is not None:
                # ignore mailto and tel links
                if next_page[0:3] == "tel":
                    continue
                elif next_page[0:6] == "mailto":
                    continue
                next_page = response.urljoin(next_page)
                # parse news page here, dont use parse?
                yield scrapy.Request(next_page, callback=self.parse, dont_filter=True)
