import scrapy
from scrapy.crawler import CrawlerProcess
# this doesn't work thanks seeking alpha, would need selenium
# from nlp_articles.app.nlp import init_nlp
settings = {}
import os

class ScraperForSeekingAlpha(scrapy.Spider):
    name = "seeking_alpha"
    start_urls = [
        "https://seekingalpha.com/market-news"
    ]

    custom_settings = {"DEPTH_LIMIT": 20}

    allowed_domains = [
        "seekingalpha"
    ]
    rate = 1

    def __init__(self):
        self.download_delay = 1/float(self.rate)
    
    # nlp = init_nlp("https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/exchanges.tsv", "https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/indicies.tsv")

    def parse(self, response):
        for link_tag in response.xpath('//a'):
            sasource = link_tag.xpath('@sasource').get()
            if sasource != None:
                if "market_news_all" in sasource or "market_news_headlines" in sasource:
                    href= link_tag.xpath('@href').extract()
                    if href is not None:
                        # ignore mailto and tel linkst
                        if href[0:3] == "tel":
                            continue
                        elif href[0:6] == "mailto":
                            continue
                        href_merged = response.urljoin(href[0])
                        yield scrapy.Request(href_merged, callback=self.handle_article, dont_filter=True)
                        break

    def handle_article(self, response):
        print("PRINTING MESSAGE")
        # get article-section
        with open('page.html', 'wb') as html_file:
            html_file.write(response.body)
        print(response)
        print("scan here")
