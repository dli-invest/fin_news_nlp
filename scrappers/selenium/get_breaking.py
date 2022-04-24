# for each key webpage, every 30 minutes grab the breaking and check and paste data into csv for initial release

import os
from selenium import webdriver
import time
from scrappers.parse_rss_cli import post_webhook_content
from bs4 import BeautifulSoup


def make_webdriver(build_name="Earnings-stock-calendar"):
    remote_url = os.environ.get("REMOTE_SELENIUM_URL")
    if remote_url == None:
        raise Exception("Missing REMOTE_SELENIUM_URL in env vars")
    desired_cap = {
        "os_version": "10",
        "resolution": "1920x1080",
        "browser": "Chrome",
        "browser_version": "latest",
        "os": "Windows",
        "name": "ES-Calendar-[Python]",  # test name
        "build": build_name,  # CI/CD job or build name
    }
    options= webdriver.ChromeOptions()
    options.capabilities.name = desired_cap.get("name", "get-breaking-[Python]")
    options.capabilities.build = desired_cap.get("build", build_name)
    driver = webdriver.Remote(
        command_executor=remote_url,
        options=options
    )
    return driver


def parse_breaking_button(html_source)-> bool:
    soup = BeautifulSoup(html_source, "html.parser")
    # get the breaking news
    breaking_button = soup.find("button", {"class": "BreakingNews-heading"})
    if breaking_button is None:
        return None
    return breaking_button

def parse_cnbc_article(html_source):
    soup = BeautifulSoup(html_source, "html.parser")
    # get the breaking news
    breaking_title = soup.find("h1").getText()
    # get the breaking news
    breaking_text = soup.find("div", {"class": "ArticleBody-articleBody"}).getText()
    # get the breaking news
    return {
        "title":breaking_title, 
        "text": breaking_text,
    }

# extract source from url using selenium at https://www.cnbc.com/
def get_breaking(url: str):
    # create a chrome webdriver
    driver = make_webdriver("Get Breaking")
    driver.get(url)
    # get the html source
    html = driver.page_source
    breaking_button = parse_breaking_button(html)
    if breaking_button is None:
        return None

    breaking_button.click()
    time.sleep(4)
    strUrl = driver.current_url

    breaking_content = driver.page_source
    # parse the html source
    content = parse_cnbc_article(breaking_content)
    breaking_title = content["title"]
    breaking_text = content["text"]
    # get the breaking news

    webhook_url = os.environ.get("DISCORD_DAILY_REVIEW_WEBHOOK")
    data = {}
    data["embeds"] = [{
        "title": breaking_title,
        "description": breaking_text[0:1900],
        "url": strUrl,
    }]
    post_webhook_content(data, webhook_url)
    return None

if __name__ == "__main__":  
    get_breaking("https://www.cnbc.com/")
