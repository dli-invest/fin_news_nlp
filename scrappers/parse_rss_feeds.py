# use beautifulsoup to scrap the following cnbc rss feed https://www.cnbc.com/id/100003114/device/rss/rss.html
from typing import List
import requests
from bs4 import BeautifulSoup

def get_feed_data(request_url: str ='https://www.cnbc.com/id/100003114/device/rss/rss.html'):
    # feeds the cnbc feeds for investing and uses beatifulsoup to parse the rss feed
    feed = requests.get(request_url)
    feed.raise_for_status()
    feed_soup = BeautifulSoup(feed.text, "xml")
    # gets the links for the cnbc feed
    feed_items = feed_soup.findAll('item')

    return feed_items

def parse_cnbc_feed(feed_items: List[dict]):
    """ grabs the data from the cnbc feed and parses it into a list of dictionaries
    """
    parsed_feed_data = []
    for item in feed_items:
        parsed_feed_data.append({
            'title': item.title.text,
            'link': item.link.text,
            'description': item.description.text,
            'pub_date': item.pubDate.text,
            'guid': item.guid.text

        })
    return parsed_feed_data


def rm_dups_from_list(list_of_dicts: List[dict]):
    """ removes duplicate entries from a list of dictionaries
    """
    # create a set of all the dictionaries in the list
    set_of_dicts = set(tuple(d.items()) for d in list_of_dicts)
    # create a list of dictionaries from the set
    list_of_dicts = [dict(d) for d in set_of_dicts]
    return list_of_dicts    


def parse_the_guardian_feed(feed_items: List[dict]):
    """ grabs data from the guardian feed and parses it into a list of dictionaries
    """
    parsed_feed_data = []
    for item in feed_items:
        # get all categories for each feed item
        categories_elements = item.findAll('category')

        # get all unique categories from categories_elements
        categories = []
        categories = [{'category': category.text, "domain": category["domain"]} for category in categories_elements]
        parsed_feed_data.append({
            'title': item.title.text,
            'link': item.link.text,
            'description': item.description.text,
            'pub_date': item.pubDate.text,
            'guid': item.guid.text,
            "categories": categories
        })
    return parsed_feed_data

def cnbc_article_to_embed(cnbc_article: dict):
    """ converts cnbc rss article to discord object
    """
    embed = {
        "title": cnbc_article['title'],
        "description": cnbc_article['description'],
        "url": cnbc_article['link'],
        "timestamp": cnbc_article['pub_date']
    }
    return embed


# links = get_feed_data()

# data = parse_cnbc_feed(links)
# # print(data)

# guardian_data = get_feed_data('https://www.theguardian.com/environment/rss')

# data = parse_the_guardian_feed(guardian_data)
# print(data)
# print(links)