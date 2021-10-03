import spacy
from app.spacy_extractor import SpacyExtractor
import pandas as pd

nlp = spacy.load("en_core_web_sm")
extractor = SpacyExtractor(nlp)

import pandas as pd


ticker_df = pd.read_csv(
            "https://raw.githubusercontent.com/dli-invest/eod_tickers/main/data/us.csv"
        )

ticker_df = ticker_df.dropna(subset=['Code', 'Name'])
ticker_df = ticker_df[~ticker_df.Name.str.contains("Wall Street", na=False)]
# remove exact matches
ticker_df = ticker_df[~ticker_df['Name'].isin(['Wall Street'])]
symbols = ticker_df.Code.tolist()
companies = ticker_df.Name.tolist()

ex_df = pd.read_csv("app/data/exchanges.tsv", sep="\t")

ind_df = pd.read_csv("app/data/indicies.tsv", sep="\t")
indexes = ind_df.IndexName.tolist()
index_symbols = ind_df.IndexSymbol.tolist()

exchanges = ex_df.ISOMIC.tolist()+ex_df["Google Prefix"].tolist()
descriptions = ex_df.Description.tolist()

stops = ["two"]
nlp = spacy.blank("en")
ruler = nlp.add_pipe("entity_ruler")
patterns = []
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#List of Entities and Patterns
for symbol in symbols:
    patterns.append({"label": "STOCK", "pattern": symbol})
    for l in letters:
        patterns.append({"label": "STOCK", "pattern": symbol+f".{l}"})
                
    
    
for company in companies:
    if company not in stops:
        patterns.append({"label": "COMPANY", "pattern": company})
        words = company.split()
        if len(words) > 1:
            new = " ".join(words[:2])
            patterns.append({"label": "COMPANY", "pattern": new})
    
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
    

ruler.add_patterns(patterns)