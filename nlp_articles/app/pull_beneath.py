import asyncio
import os
import beneath
import json
import time
from datetime import datetime, timedelta
from nlp_articles.app.nlp import init_nlp
# move post_webhook_content to a separate file inside nlp_articles.core
from scrappers.parse_rss_cli import post_webhook_content

async def callback(record):
    print(record)

async def main():
    beneathKey = os.getenv("BENEATH_SECRET")
    client = beneath.Client(secret=beneathKey)
    table = await client.find_table("examples/reddit/r-wallstreetbets-posts")
    table_instance = await table.find_instances()
    first_instance = table_instance[0]

    start_date = datetime.today() - timedelta(hours=0, minutes=400)
    start_time_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    end_time_str = datetime.today().strftime('%Y-%m-%dT%H:%M:%S')
    filter = json.dumps({"created_on": { "_gte": start_time_str, "_lt": end_time_str}})
    cursor = await first_instance.query_index(filter=filter)
    records = await cursor.read_all()
    if len(records) > 0:
        nlp = init_nlp("https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/exchanges.tsv", "https://raw.githubusercontent.com/dli-invest/fin_news_nlp/main/nlp_articles/core/data/indicies.tsv")
        # iterate through records
        # create spacy documents using records
        discord_embeds = []
        beneath_hits = 0
        for record in records:
            text = record.get("text")
            author = record.get("author")
            created_on = record.get("created_on")
            permalink = record.get("permalink")
            # make a spacy document
            comment_doc = nlp(text)
            entity_hits = len(comment_doc.ents)
            fields = [ {"name": entity.label_, "value": entity.text, "inline": True} for entity in comment_doc.ents]
            if entity_hits >= 1:
                embed = {
                    "title": f"wsb | {author}",
                    "description": text[:1800],
                    "url": f"https://reddit.com/{permalink}",
                    "fields": fields[:3],
                }
                # Additionally, the characters in all title, description, field.name, field.value, footer.text, and author.name fields must not exceed 6000 characters in total. Violating any of these constraints will result in a Bad Request response.
                discord_embeds.append(embed)
                if len(discord_embeds) >= 3:
                    beneath_hits += len(discord_embeds)
                    post_webhook_content({"embeds": discord_embeds})
                    discord_embeds = []
                    time.sleep(2)
                    # if len(discord_embeds) >= 9:
                    #     print(discord_embeds)
                    #     post_webhook_content({"embeds": discord_embeds})
                    # send if any hits are available
        if discord_embeds:
            post_webhook_content({"embeds": discord_embeds})
            discord_embeds = []
            beneath_hits += len(discord_embeds)
            time.sleep(2)

        GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
        GITHUB_RUN_ID = os.environ.get("GITHUB_RUN_ID")
        run_url = f"https://github.com/{GITHUB_REPOSITORY}/actions/runs/{GITHUB_RUN_ID}"
        embeds = {"embeds": [{"title": "fin_news_nlp | Beneath /r/wsb", "description": f"Total Reddit Posts: {beneath_hits}", "color": 0x0000ff, "url": run_url}]}
        post_webhook_content(embeds, "DISCORD_STATS_WEBHOOK")
        # exit on error based on environment variable EXIT_ON_ERROR
        if os.getenv("EXIT_ON_ERROR") == "true":
            exit(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
