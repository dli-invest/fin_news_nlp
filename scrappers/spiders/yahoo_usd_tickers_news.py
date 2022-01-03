import pandas as pd
import scrapy
from scrapy import signals
import re
import requests
import os
from datetime import datetime
import dateparser
import json
from scrappers.get_tickers import TickerControllerV2
from bs4 import BeautifulSoup
from nlp_articles.app.nlp import init_nlp

output_file = "data/yahoo_usd_tickers.csv"

nlp = init_nlp("https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/exchanges.tsv", "https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/indicies.tsv")

class YahooUSDStockSpider(scrapy.Spider):
    name = "usd_stock_news"
    base_yahoo_url = "https://ca.finance.yahoo.com/quote"
    ticker_controller = TickerControllerV2({
        "default_url": "https://raw.githubusercontent.com/dli-invest/eod_tickers/main/data/us_stock_data.csv",
        "tickers_config": {
            "price": 5E4,
            "market_cap": 1E13,
        }
    })
    should_visit_news_articles = False
    current_date = datetime.now()
    embeds_in_queue = []
    webhook = os.environ.get('DISCORD_WEBHOOK')
    if webhook == None:
        print("REQUIRE DISCORD WEBHOOK")
        exit(1)
    # redirect urls, need to clean up in data
    redirect_urls = []

    # if output file exists
    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
    else: 
        df = pd.DataFrame(columns=["url", "stock"])

    def start_requests(self):
        tickers = self.ticker_controller.get_ytickers()
        yahoo_urls = [f"{self.base_yahoo_url}/{ticker}" for ticker in tickers]
        urls = yahoo_urls
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
            if len(self.embeds_in_queue) >= 8:
                data = {
                    "username": "fin_news_nlp/yahoo_cad_tickers_news",
                }
                data["embeds"] = self.embeds_in_queue
                self.embeds_in_queue = []
                self.post_webhook_content(data)

    def parse(self, response):
        try:
            url = response.url
            if response.status == 302:
                self.redirect_urls.append(url)
                return None

            page_title = url.rsplit('/', 1)[1]
            page_title = page_title[:-4]
            page_title = page_title.replace("-", " ")
            page_title = re.sub(r"d+$", "", page_title)
            page_title = self.upper_case(page_title)
            ticker = url.rsplit('/', 1)[-1]
            # rework this scrapping logic to only use BeautifulSoup
            full_soup = BeautifulSoup(response.body, features="lxml")
            news_items = full_soup.find_all("li", {"class": "js-stream-content"})
            for item in news_items[0:2]:
                embed_item = self.parse_news_item(item, response)
                if embed_item is not None:
                    embed_url = embed_item.get('url')
                    if embed_url not in self.df["url"]:
                        self.embeds_in_queue.append(embed_item)
                        # add row to dataframe
                        self.df = self.df.append({"url": embed_url, "stock": ticker}, ignore_index=True)
                    # if len(self.embeds_in_queue) >= 9:
                    #     data = {}
                    #     data["embeds"] = self.embeds_in_queue
                    #     self.embeds_in_queue = []
                    #     self.post_webhook_content(data)
        except Exception as e:
            os.environ["EXIT_ON_ERROR"] = "true"
            pass

    @staticmethod      
    def upper_case(str):
        return re.sub(r"(_|-)+", " ", str).title()

    def get_news_provider(self, item: dict):
        try:
            return item.select("li div div > div:nth-child(2) > div")
        except Exception as e:
            return "N/A"
    
    def parse_news_item(self, item: dict, response):
        link = item.find("a", {"class": "js-content-viewer"})
        if link is None:
            return None
        # print(item)
        news_provider = self.get_news_provider(item)
        provider = news_provider[0].text
        # article_date = dateparser.parse(date_posted)
        # diff_date = self.current_date - article_date
        url_text = link.text
        url = link["href"]
        href_merged = response.urljoin(url)
        description = item.find("p").text
        # apply nlp to both url_text and description
        url_text_doc = nlp(url_text)
        description_doc = nlp(description)
        entities = description_doc.ents + url_text_doc.ents
        # count number of entities in the description and title
        entity_hits = len(entities)
        # make fields for the embed from ents
        fields = [description_doc.ents, url_text_doc.ents]
        # make a list of all the entities
        if entity_hits >= 5:
            fields = [ {"name": entity.label_, "value": entity.text, "inline": True} for entity in entities]
            return {
                "url": href_merged,
                "title": f"{provider} - {url_text}",
                "description": description,
                "fields": fields
            }
        return None

    def handle_article(self, response):
        url = response.url
        page_title = url.rsplit('/', 1)[1]
        page_title = page_title[:-4]
        page_title = page_title.replace("-", " ")
        # rework this scrapping logic to only use BeautifulSoup
        full_soup = BeautifulSoup(response.body, features="lxml")
        timestamp = full_soup.find('time').text
        article_date = dateparser.parse(timestamp)
        current_date = datetime.now()
        body = response.css('div.caas-body-section div.caas-content div.caas-body').get()
        soup = BeautifulSoup(body, features="lxml")
        article_data = soup.text
        article_data.\
            replace("Story continues.", "").\
            replace("Download the Yahoo Finance app, available for Apple and Android.", "")
        doc = nlp(article_data)
        entities = []
        has_critical_term = False
        for ent in doc.ents:
            if ent.label_ == "CRITICAL":
                has_critical_term = True
            entities.append({
                "text": ent.text,
                "label": ent.label_
            })
        entities = [dict(t) for t in {tuple(d.items()) for d in entities}]
        diff_date = current_date - article_date
        # map entities to fields
        embeds = []
        fields = []
        data = {}
        if diff_date.seconds // 3600 < 24:
            # send article to discord
            # map data to embeds
            for ent in entities[:24]:
                fields.append({
                    "name": ent.get("text"),
                    "value": ent.get("label"),
                    "inline": True
                })
            first_sentence = article_data[:100]
            # MAP type to color
            embed = {
                # "color": color,
                "title": page_title,
                "timestamp": article_date.isoformat(),
                "url": url,
                "fields": fields,
                "description": first_sentence
            }
            embeds.append(embed)
            data["embeds"] = embeds
            self.post_webhook_content(data)



    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(YahooUSDStockSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_opened, signals.spider_opened)
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_opened(self, spider):
        print("spider opened")

    def spider_closed(self, spider):
        self.df.to_csv(output_file, index=False)

        # exit if os env is set
        if os.environ.get("EXIT_ON_ERROR") == "true":
            exit(1)

    def post_webhook_content(self, data: dict):
        url = self.webhook

        result = requests.post(
            url, data=json.dumps(data), headers={"Content-Type": "application/json"}
        )

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))