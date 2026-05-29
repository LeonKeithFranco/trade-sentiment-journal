import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import itertools
    import json
    import random

    import numpy as np
    from datasets import load_dataset, load_from_disk
    from utils import constants
    from utils.preprocess import process_full_dataset_sentences

    return (
        constants,
        itertools,
        json,
        load_dataset,
        load_from_disk,
        np,
        process_full_dataset_sentences,
        random,
    )


@app.cell
def _(constants, load_dataset, load_from_disk, process_full_dataset_sentences):
    DATASET_NAME = "lmassaron/FinancialPhraseBank"

    if constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH.exists():
        full_dataset = load_from_disk(constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH)
    else:
        full_dataset = load_dataset(DATASET_NAME)
        full_dataset = process_full_dataset_sentences(full_dataset)
        full_dataset.save_to_disk(constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH)

    full_dataset
    return (full_dataset,)


@app.cell
def _(full_dataset):
    train_vocab = set()

    for data in full_dataset["train"]:
        for part in data["sentence"].split(" "):
            train_vocab.add(part)

    train_vocab
    return (train_vocab,)


@app.cell
def _(constants):
    with open(constants.GLOVE_EMBEDDINGS_FILE_PATH, "r") as f:
        glove_file_contents = f.readlines()

    glove_file_contents[0:5]
    return (glove_file_contents,)


@app.cell
def _(glove_file_contents, itertools):
    glove_words = set()

    for line in glove_file_contents:
        glove_words.add(line.split(" ")[0])

    set(itertools.islice(glove_words, 5))
    return (glove_words,)


@app.cell
def _(glove_words, train_vocab):
    vocab = train_vocab & glove_words
    vocab
    return (vocab,)


@app.cell
def _(vocab):
    vocab_mapping = {
        "<PAD>": 0,
        "<UNK>": 1,
        "<NUM>": 2,
    }

    num_special_tokens = len(vocab_mapping)

    for i, word in enumerate(vocab):
        vocab_mapping[word] = i + num_special_tokens

    vocab_mapping
    return (vocab_mapping,)


@app.cell
def _(constants, json, vocab_mapping):
    if not constants.VOCAB_MAPPING_FILE_PATH.exists():
        with open(constants.VOCAB_MAPPING_FILE_PATH, "w") as ff:
            json.dump(vocab_mapping, ff, indent=4)

    constants.VOCAB_MAPPING_FILE_PATH.exists()
    return


@app.cell
def _(constants, glove_file_contents, np, random, vocab_mapping):
    if not constants.MATRIX_EMBEDDINGS_FILE_PATH.exists():
        random.seed(42)

        vectors = [[] for _ in range(len(vocab_mapping))]
        embedding_length = len(glove_file_contents[0].split(" ")[1:])

        vectors[0] = ["0.0"] * embedding_length
        vectors[1] = [str(random.uniform(-1, 1)) for _ in range(embedding_length)]
        vectors[2] = [str(random.uniform(-1, 1)) for _ in range(embedding_length)]

        for lline in glove_file_contents:
            parts = lline.split(" ")

            wword = parts[0]

            if wword not in vocab_mapping:
                continue

            embedding = parts[1:]

            vectors[vocab_mapping[wword]] = embedding

        vectors = np.array(vectors, dtype=np.float32)

        np.save(constants.MATRIX_EMBEDDINGS_FILE_PATH, vectors)

    vectors[:5]
    return


if __name__ == "__main__":
    app.run()
