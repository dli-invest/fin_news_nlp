import os
import scrapy
from scrapy.crawler import CrawlerProcess
# this doesn't work thanks seeking alpha, would need selenium
# from nlp_articles.app.nlp import init_nlp
settings = {}

import os

LOCAL_FILENAME = 'example.html'
LOCAL_FOLDER = 'html_files'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ScraperForYahoo(scrapy.Spider):
    name = "test_yahoo_finance"
    start_urls = [
        "https://ca.finance.yahoo.com/"
    ]
    start_urls = [
        f"file://{BASE_DIR}/{LOCAL_FOLDER}/index.html"
    ]

    custom_settings = {"DEPTH_LIMIT": 20}

    rate = 0.1

    def __init__(self):
        self.download_delay = 1/float(self.rate)

    # nlp = init_nlp("https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/exchanges.tsv", "https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/indicies.tsv")

    def parse(self, response):
        for a_tag in response.css('a.js-content-viewer'):
            href = a_tag.attrib["href"]
            if href is not None:
                # ignore mailto and tel linkst
                if href[0:3] == "tel":
                    continue
                elif href[0:6] == "mailto":
                    continue
                print(href)
                href_merged = response.urljoin(href)
                yield scrapy.Request(href_merged, callback=self.handle_article, dont_filter=True)
                break

    def handle_article(self, response):
        print("PRINTING MESSAGE")
        # get article-section
        with open('page.html', 'wb') as html_file:
            html_file.write(response.body)
        print(response)
        print("scan here")
