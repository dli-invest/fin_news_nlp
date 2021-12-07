# in main function get list of rss links and parse them
import requests
import json
import os
import time
from scrappers.parse_rss_feeds import get_feed_data, cnbc_article_to_embed, parse_cnbc_feed, parse_the_guardian_feed
from nlp_articles.app.nlp import init_nlp
total_hits = 0

def parse_output_file(output_file = "cnbc_urls.txt"):
    """parse an output files and read the files"""

    articles = []
    try:
        with open(output_file) as file_in:
            for line in file_in:
                clean_line = line.replace("\n", "")
                articles.append(clean_line)
    except Exception as e:
        pass
    return articles

def save_list_of_strs_to_file(read_articles, file_name = "cnbc_urls.txt"):
    """save list of strings to file"""

    clean_list = list( dict.fromkeys(read_articles) )
    if clean_list:
        with open(file_name, 'w') as txt_file:
            for article_url in clean_list:
                txt_file.write(article_url +"\n")

def post_webhook_content(data: dict, webhook_env = "DISCORD_WEBHOOK"):
        print("SENDING DATA")
        url = os.environ.get(webhook_env)

        result = requests.post(
            url, data=json.dumps(data), headers={"Content-Type": "application/json"}
        )

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            print("Payload delivered successfully, code {}.".format(result.status_code))

def iterate_cnbc_feed(cnbc_feed, nlp, cnbc_read_articles, discord_embeds):
    global total_hits
    for cnbc_article in cnbc_feed:
        cnbc_data = cnbc_article_to_embed(cnbc_article)
        try:
            description_doc = nlp(cnbc_article["description"])
            title_doc = nlp(cnbc_article["title"])
            entities = description_doc.ents + title_doc.ents
            # count number of entities in the description and title
            entity_hits = len(entities)
            # make fields for the embed from ents
            fields = [description_doc.ents, title_doc.ents]
            # make a list of all the entities
            fields = [ {"name": entity.label_, "value": entity.text, "inline": True} for entity in entities]
            cnbc_data["fields"] = fields[:10]
            if entity_hits >= 1:
                discord_embeds.append(cnbc_data)
                if len(discord_embeds) >= 4:
                    total_hits += len(discord_embeds)
                    post_webhook_content({"embeds": discord_embeds})
                    discord_embeds = []
                    time.sleep(2)
                cnbc_read_articles.append(cnbc_article['link'])
        except Exception as e:
            print(e)
            continue
def main():
    global total_hits
    # init nlp 
    nlp = init_nlp("https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/exchanges.tsv", "https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/indicies.tsv")
    # read json from file "data/cnbc_feeds.json"
    with open("data/cnbc_feeds.json") as feeds_file:
        cnbc_feeds = json.load(feeds_file)
    the_guardian_feed_urls = []
    # the_guardian_feed_urls = ["https://www.theguardian.com/environment/rss"]
    stock_feed_list = [*cnbc_feeds.get("feeds"), *the_guardian_feed_urls]

    cnbc_output = "data/cnbc_urls.txt"
    cnbc_read_articles = parse_output_file(cnbc_output)
    # accumulate all the cnbc and the guardian feeds
    discord_embeds = []
    for feed_data in stock_feed_list:
        feed_url = feed_data.get("feedUri")
        rss_feed = get_feed_data(feed_url)
        if feed_url.startswith("https://www.cnbc.com"):
            if feed_url not in cnbc_read_articles:
                cnbc_feed = parse_cnbc_feed(rss_feed)
                iterate_cnbc_feed(cnbc_feed, nlp, cnbc_read_articles, discord_embeds)
            # check if article is seen before
        # eventually move the guardian article logic to the guardian api
        elif feed_url.startswith("https://www.theguardian.com"):
            guardian_article = parse_the_guardian_feed(rss_feed)
            continue

        if len(discord_embeds) >= 4:
            post_webhook_content({"embeds": discord_embeds})
            total_hits = total_hits + len(discord_embeds)
            discord_embeds = []

    save_list_of_strs_to_file(cnbc_read_articles)
    embeds = {"embeds": [{"title": "fin_news_nlp | parse_rss_cli - cnbc", "description": f"Total Hits {total_hits}", "color": 0x00ff00}]}
    post_webhook_content(embeds, "DISCORD_STATS_WEBHOOK")
if __name__ == '__main__':
    main()
