import re


def process_text(text):
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        try:
            words = word_tokenize(text)
            stops = set(stopwords.words("english"))
        except LookupError:
            nltk.download("punkt", quiet=True)
            nltk.download("punkt_tab", quiet=True)
            nltk.download("stopwords", quiet=True)
            words = word_tokenize(text)
            stops = set(stopwords.words("english"))
    except ImportError:
        words = re.findall(r"\b\w+\b", text)
        stops = {"the", "a", "an", "and", "or", "is", "at", "to", "of", "in", "for", "on"}
    clean = [w for w in words if w.lower() not in stops]
    keywords = sorted({w.lower() for w in clean if w.isalnum()})
    return words, clean, keywords


def search_relevant_expenses(trip, query):
    query = query.lower().strip()
    matches = []
    for e in trip.expenses:
        text = f"{e.name} {e.category} {e.description}"
        if query in text.lower():
            matches.append(e)
    return matches
