import requests
import os

def map_embed_to_article(articleData: dict)-> dict:
    """
    Take an article and map the embed to the article
    """
    article = {
        "source": articleData["username"],
        "title": articleData["title"],
        "url": articleData["url"],
        "description": articleData["description"],
    }
    if "exchange" in articleData:
        article["exchange"] = articleData["exchange"]
    if "country" in articleData:
        article["country"] = articleData["country"]
    if "author" in articleData:
        article["author"] = articleData["author"]

    if "company" in articleData:
        article["company"] = articleData["company"]

    return article

# send data to https://dli-fauna-gql.deno.dev/articles
def send_data_to_fauna(article: dict)-> None:
    """
    Take ArticleData and send it to 
    """
    base_url = os.environ.get("FAUNA_URL")
    url = f"{base_url}/articles"
    r = requests.post(url, json=article)
    # check if the request was successful
    if r.status_code == 201 or r.status_code == 200:
        print("Successfully sent to fauna")
    else:
        print(f"Error sending to fauna: {r.status_code}")


def map_and_send_embeds_to_fauna(embeds: list, **kwargs)-> None:
    """
    Take a list of embeds and map them to articles and send them to fauna
    """
    for embed in embeds:
        for key, value in kwargs.items():
            embed[key] = value
        article = map_embed_to_article(embed)
        send_data_to_fauna(article)
