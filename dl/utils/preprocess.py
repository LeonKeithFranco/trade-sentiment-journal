import string
from typing import cast

import nltk
from datasets.arrow_dataset import Dataset
from datasets.dataset_dict import DatasetDict
from nltk.tokenize import word_tokenize

_TOKENIZER_FILE = "punkt_tab"

try:
    nltk.data.find(f"tokenizers/{_TOKENIZER_FILE}")
except LookupError:
    nltk.download(_TOKENIZER_FILE)


def _is_number(s: str) -> bool:
    try:
        float(s.replace(",", ""))
        return True
    except ValueError:
        return False


def process_sentence(sentence: str) -> str:
    tokens = []

    initial = cast(list[str], word_tokenize(sentence.lower()))
    for token in initial:
        if all(char in string.punctuation for char in token):
            continue

        if "www." in token:
            continue

        if any(ord(char) > 127 for char in token):
            continue

        if _is_number(token):
            token = "<NUM>"

        tokens.append(token)

    return " ".join(tokens)


def process_dataset_sentences(dataset: Dataset) -> Dataset:
    return dataset.map(lambda data: {"sentence": process_sentence(data["sentence"])})


def process_full_dataset_sentences(full_dataset: DatasetDict) -> DatasetDict:
    return DatasetDict(
        {split: process_dataset_sentences(data) for split, data in full_dataset.items()}
    )
