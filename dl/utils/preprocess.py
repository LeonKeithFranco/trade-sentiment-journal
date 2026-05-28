import string

import nltk
from nltk.tokenize import word_tokenize

nltk.download("punkt_tab")


def process_sentence(sentence: str) -> str:
    tokens = [
        token
        for token in word_tokenize(sentence.lower())
        if token not in string.punctuation
    ]

    return " ".join(tokens)
