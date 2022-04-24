# fin_news_nlp
Financial nlp project to scan news sites for information built using spacy, fastapi, scrapy, cookercutter and various news sources. Also scan for breaking news.

## NLP

Use spacy to analyze financial articles

To test run:
```
cd nlp_articles
pytest
```

## Scrapy

scan websites for articles in real time, this repo contains the scraper


scrap crawl yahoo_finance

### TODO

- helper script to extract data from urls after the fact.
- ~~add long-term csv file to track articles and keywords~~.
- ~~clear temporary csv file in temporary jobs~~.
