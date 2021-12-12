import spacy
import pandas as pd

def init_nlp(exchange_data_path: str, indicies_data_path: str):
    nlp = spacy.load("en_core_web_sm")
    ticker_df = pd.read_csv(
                "https://raw.githubusercontent.com/dli-invest/eod_tickers/main/data/us.csv"
            )

    ticker_df = ticker_df.dropna(subset=['Code', 'Name'])
    ticker_df = ticker_df[~ticker_df.Name.str.contains("Wall Street", na=False)]
    # remove exact matches
    ticker_df = ticker_df[~ticker_df['Name'].isin(['Wall Street'])]
    # remove bad symbols
    ticker_df = ticker_df[~ticker_df['Code'].isin(['ET'])]
    symbols = ticker_df.Code.tolist()
    companies = ticker_df.Name.tolist()

    ex_df = pd.read_csv(exchange_data_path, sep="\t")

    ind_df = pd.read_csv(indicies_data_path, sep="\t")
    indexes = ind_df.IndexName.tolist()
    index_symbols = ind_df.IndexSymbol.tolist()

    exchanges = ex_df.ISOMIC.tolist()+ ex_df["Google Prefix"].tolist()
    descriptions = ex_df.Description.tolist()

    stops = ["two", "the", "u.s.", "wall", "data", "ceo", "build", "better", "office", "service", "north", "canadian", "chinese", "communist", "new", "can", "good", "in", "here", "all", "social media", "hope", "party", "america", "president", "hot", "white", "house", "tuesday"]
    nlp = spacy.blank("en")
    ruler = nlp.add_pipe("entity_ruler")
    patterns = []

    first_words_added = []
    endings = [".TO", ".V", ".CN", ".HK"]
    #List of Entities and Patterns
    for symbol in symbols:
        if len(symbol) > 1:
            patterns.append({"label": "STOCK", "pattern": symbol})
            for ending in endings:
                patterns.append({"label": "STOCK", "pattern": symbol+f".{ending}"})



    for company in companies:
        if company not in stops and len(company) > 1:
            patterns.append({"label": "COMPANY", "pattern": company})
            words = company.split()
            if len(words) >= 1:
                new = " ".join(words[:2])
                patterns.append({"label": "COMPANY", "pattern": new})
                # add first word to list as well
                first_word = words[0]
                # ignore the numbers
                if first_word.isnumeric() == False and first_word.lower() not in stops:
                    if first_word not in first_words_added:
                        first_words_added.append(first_word)
                        patterns.append({"label": "COMPANY", "pattern": words[0]})

    for index in indexes:
        patterns.append({"label": "INDEX", "pattern": index})
        versions = []
        words = index.split()
        caps = []
        for word in words:
            word = word.lower().capitalize()
            caps.append(word)
        versions.append(" ".join(caps))
        versions.append(words[0])
        versions.append(caps[0])
        versions.append(" ".join(caps[:2]))
        versions.append(" ".join(words[:2]))
        for version in versions:
            if version != "NYSE":
                patterns.append({"label": "INDEX", "pattern": version})

    for symbol in index_symbols:
        patterns.append({"label": "INDEX", "pattern": symbol})    


    for d in descriptions:
        patterns.append({"label": "STOCK_EXCHANGE", "pattern": d})
    for e in exchanges:
        patterns.append({"label": "STOCK_EXCHANGE", "pattern": e})

    for crit in ["evergrande", "climate", "recession", "depression", "FED"]:
         patterns.append({"label": "CRITICAL", "pattern": crit})

    for term in ["COP", "BIDEN"]:
        patterns.append({"label": "EVENT", "pattern": term})

    for country in ["USA", "US", "United States", "U.S.", "U.S.A.", "CANADA", "CHINA"]:
        patterns.append({"label": "COUNTRY", "pattern": country})
    # might be of interest 

    for ec in ["ENVIRONMENT", "INTEREST", "RATES", "TAXPAYERS", "TRUMP", "SUPPLY"]:
        patterns.append({"label": "MAYBE", "pattern": ec})
    ruler.add_patterns(patterns)
    return nlp