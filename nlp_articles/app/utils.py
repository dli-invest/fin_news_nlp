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
                "even", "back", "any", "good", "gen", "all"
                ]

geolocation_words = ["america", "u.s", "canadian", "chinese",
                     "white", "house", "city", "louisiana", "georgia", "us"]

political_terms = ["communist", "white", "house", "president", "party"]
business_terms = ["wall", "ceo", "techology", "labor"]
mishits = ["z", "x", "tuesday", "family", "funding",
           "free", "contact", "health", "doctor", "web", "crazy", "for", "help"]

stop_terms = [
    *common_words,
    *geolocation_words,
    *political_terms,
    *business_terms,
    *mishits
]
