import string

import nltk
from nltk.tokenize import word_tokenize

_TOKENIZER_FILE = "punkt_tab"

try:
    nltk.data.find(f"tokenizers/{_TOKENIZER_FILE}")
except LookupError:
    nltk.download(_TOKENIZER_FILE)


def process_sentence(sentence: str) -> str:
    tokens = [
        token
        for token in word_tokenize(sentence.lower())
        if token not in string.punctuation
    ]

    return " ".join(tokens)
