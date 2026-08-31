import json
import string
from functools import lru_cache
from typing import cast

import nltk
from datasets.arrow_dataset import Dataset
from datasets.dataset_dict import DatasetDict
from nltk.tokenize import word_tokenize

from dl import constants

_TOKENIZER_FILE = "punkt_tab"

try:
    nltk.data.find(f"tokenizers/{_TOKENIZER_FILE}")
except LookupError:
    nltk.download(_TOKENIZER_FILE)


def _is_number(s: str) -> bool:
    """Check whether a string can be parsed as a number, allowing thousands separators.

    Args:
        s: The string to check.

    Returns:
        bool: True if the string can be parsed as a float once commas are
            removed, False otherwise.
    """
    try:
        float(s.replace(",", ""))
        return True
    except ValueError:
        return False


def process_sentence(sentence: str) -> str:
    """Clean and tokenize a sentence for model input.

    Lowercases the sentence, tokenizes it, and drops pure-punctuation
    tokens, URL fragments, and non-ASCII tokens. Numeric tokens are
    normalized to a shared "<NUM>" placeholder.

    Args:
        sentence: The raw sentence to process.

    Returns:
        str: The cleaned sentence, with tokens joined by single spaces.
    """
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
    """Apply sentence preprocessing to every row of a single dataset split.

    Args:
        dataset: The dataset split whose "sentence" column should be
            processed.

    Returns:
        Dataset: The dataset with its "sentence" column replaced by the
            cleaned, tokenized text.
    """
    return dataset.map(lambda data: {"sentence": process_sentence(data["sentence"])})


def process_full_dataset_sentences(full_dataset: DatasetDict) -> DatasetDict:
    """Apply sentence preprocessing to every split of a dataset.

    Args:
        full_dataset: The dataset, containing one or more splits (e.g.
            train, validation, test).

    Returns:
        DatasetDict: The dataset with every split's "sentence" column
            replaced by the cleaned, tokenized text.
    """
    return DatasetDict(
        {split: process_dataset_sentences(data) for split, data in full_dataset.items()}
    )


@lru_cache
def get_vocab_mapping() -> dict[str, int]:
    """Load and cache the token-to-vocabulary-index mapping from disk.

    Returns:
        dict[str, int]: A mapping from token strings to their integer
            vocabulary index.

    Raises:
        FileNotFoundError: If the vocab mapping file does not exist.
    """
    if not constants.VOCAB_MAPPING_FILE_PATH.exists():
        raise FileNotFoundError(
            f"{constants.VOCAB_MAPPING_FILE_PATH.name} not found. Please run get_and_cache_data.py to generate the file"
        )

    with open(constants.VOCAB_MAPPING_FILE_PATH, "r") as f:
        return cast(dict[str, int], json.load(f))


def map_sentence(sentence: str) -> list[int]:
    """Convert a space-tokenized sentence into a list of vocabulary indices.

    Unknown tokens are mapped to the "<UNK>" index.

    Args:
        sentence: A preprocessed, space-separated sentence.

    Returns:
        list[int]: The vocabulary indices for each token in the sentence, or
            an empty list if the sentence has no tokens.
    """
    mapping = get_vocab_mapping()

    tokens = sentence.split(" ")

    if (len(tokens) == 1) and (tokens[0] == ""):
        return []

    mapped_sentence = [mapping.get(token, mapping["<UNK>"]) for token in tokens]

    return mapped_sentence


def process_and_map_sentence(sentence: str) -> list[int]:
    """Clean, tokenize, and map a raw sentence to model input IDs.

    Args:
        sentence: The raw sentence to process.

    Returns:
        list[int]: The vocabulary indices for each token in the processed
            sentence, or an empty list if the sentence has no tokens.
    """
    sentence = process_sentence(sentence)
    return map_sentence(sentence)
