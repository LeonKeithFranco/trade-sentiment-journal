import json
import string
from functools import lru_cache
from typing import cast

import nltk
from datasets.arrow_dataset import Dataset
from datasets.dataset_dict import DatasetDict
from nltk.tokenize import word_tokenize

from utils import constants

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


@lru_cache
def get_vocab_mapping() -> dict[str, int]:
    if not constants.VOCAB_MAPPING_FILE_PATH.exists():
        raise FileNotFoundError(
            f"{constants.VOCAB_MAPPING_FILE_PATH.name} not found. Please run get_and_cache_data.py to generate the file"
        )

    with open(constants.VOCAB_MAPPING_FILE_PATH, "r") as f:
        return cast(dict[str, int], json.load(f))


def map_sentence(sentence: str) -> list[int]:
    mapping = get_vocab_mapping()

    tokens = sentence.split(" ")

    if (len(tokens) == 1) and (tokens[0] == ""):
        return []

    mapped_sentence = [mapping.get(token, mapping["<UNK>"]) for token in tokens]

    return mapped_sentence


def process_and_map_sentence(sentence: str) -> list[int]:
    sentence = process_sentence(sentence)
    return map_sentence(sentence)
