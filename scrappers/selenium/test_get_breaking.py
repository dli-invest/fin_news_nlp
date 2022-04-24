from scrappers.selenium.get_breaking import  parse_cnbc_article, parse_breaking_button


if __name__ == "__main__":
    # read html from breaking.html
    with open("scrappers/selenium/breaking.html", "r") as f:
        html = f.read()
    result = parse_breaking_button(html)
    assert result is not None
    with open("scrappers/selenium/france.html", "r") as f:
        html = f.read()
    result = parse_cnbc_article(html)
    print(result)
    assert result is not None
    # get_breaking(url)