import string

import nltk
from datasets.arrow_dataset import Dataset
from datasets.dataset_dict import DatasetDict
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


def process_dataset_sentences(dataset: Dataset) -> Dataset:
    return dataset.map(lambda data: {"sentence": process_sentence(data["sentence"])})


def process_full_dataset_sentences(full_dataset: DatasetDict) -> DatasetDict:
    return DatasetDict(
        {split: process_dataset_sentences(data) for split, data in full_dataset.items()}
    )
