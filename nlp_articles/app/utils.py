common_words = ["the", "two", "free", "family", "no", "z",
                "in", "here", "all", "hot", "fox", "data", "of",
                "and", "to", "a", "for", "on", "with", "is", "in",
                "that", "by", "as", "it", "you", "this", "be",
                "at", "have", "from", "or", "an", "was", "but",
                "not", "he", "she", "are", "we", "they", "were",
                "what", "when", "where", "which", "who", "how",
                "why", "can", "will", "if", "would", "one", "all",
                "any", "other", "use", "word", "than", "new",
                "some", "make", "about", "time", "look", "people",
                "into", "just", "see", "him", "your", "come", "day",
                "than", "know", "think", "take", "people", "see", "get",
                "now", "help", "work", "may", "part", "year", "such",
                "give", "me", "find", "call", "good", "very", "still",
                "am", "here", "work", "last", "own", "too",
                "even", "back", "any", "good", "gen", "all",
                "hi"
                ]

geolocation_words = ["america", "u.s", "canadian", "chinese",
                     "white", "house", "city", "louisiana", "georgia", "us", "u.s.", 
                     "american"]

political_terms = ["communist", "white", "house", "president", "party"]
business_terms = ["wall", "ceo", "techology", "labor"]
mishits = ["z", "x", "tuesday", "family", "funding",
           "free", "contact", "health", "doctor", "web", "crazy",
           "for", "help", "card", "financial",
           "consensus", "critical",
           "Partners", "climate", "boomer",
           "Investor", "Growth", "Dividend",
           "Treasury", "Bell", "Eve", "Big", "Tech", "Five", "Bank"
        ]
# search for S3 partners
stop_terms = [
    *common_words,
    *geolocation_words,
    *political_terms,
    *business_terms,
    *mishits
]

S3_PARTNERS = [
    {"LOWER": "s3"},
    {"TEXT": {"REGEX": "^[Pp](.?|artner)?"}}
]

DIVIDEND_LABEL = "DIVIDENDS"

cse_pattern = [
    {"TEXT": {"REGEX": "(?i)CSE|CVE"}},
    {"IS_PUNCT": True, "OP": "?"}
]

tsx_pattern = [
    {"TEXT": {"REGEX": "TSX|TSXV"}},
    {"TEXT": ":", "OP": "?"},
    {"IS_PUNCT": True, "OP": "?"},
    {"TEXT": {"REGEX": "\w"}},
]
