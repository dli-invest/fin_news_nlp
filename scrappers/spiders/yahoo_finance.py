import os
import scrapy
import dateparser
import requests
import json
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
# this doesn't work thanks seeking alpha, would need selenium
from nlp_articles.app.nlp import init_nlp
settings = {}

nlp = init_nlp("https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/exchanges.tsv", "https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/indicies.tsv")


class ScraperForYahoo(scrapy.Spider):
    name = "yahoo_finance"
    start_urls = [
        "https://ca.finance.yahoo.com/"
    ]

    custom_settings = {"DEPTH_LIMIT": 20}

    allowed_domains = [
        "yahoo",
        "ca.finance.yahoo"
    ]
    read_article_urls = []
    rate = 2
    webhook =  os.getenv('DISCORD_WEBHOOK')

    def __init__(self):
        self.download_delay = 1/float(self.rate)

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
        if diff_date.seconds // 3600 < 1.1:
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
            self.read_article_urls.append(url)

            print("_________________________________")
            print(self.read_article_urls)
            print("---------------------------------")


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
