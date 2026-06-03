import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import random

    import numpy as np
    from dl.get_dataset import get_dataset
    from numpy.typing import NDArray

    from dl import constants

    return NDArray, constants, get_dataset, json, np, random


@app.cell
def _(get_dataset):
    full_dataset = get_dataset()
    return (full_dataset,)


@app.cell
def _(constants):
    with open(constants.GLOVE_EMBEDDINGS_FILE_PATH, "r") as f:
        glove_file_contents = f.readlines()

    glove_file_contents[0:5]
    return (glove_file_contents,)


@app.cell
def _(full_dataset):
    def get_train_vocab() -> set[str]:
        train_vocab = set()

        for data in full_dataset["train"]:
            for part in data["sentence"].split(" "):
                train_vocab.add(part)

        return train_vocab

    return (get_train_vocab,)


@app.cell
def _(glove_file_contents):
    def get_glove_words() -> set[str]:
        glove_words = set()

        for line in glove_file_contents:
            glove_words.add(line.split(" ")[0])

        return glove_words

    return (get_glove_words,)


@app.cell
def _(constants, get_glove_words, get_train_vocab, json):
    def get_vocab_mapping() -> dict[str, int]:
        vocab = get_train_vocab() & get_glove_words()

        vocab_mapping = {
            "<PAD>": 0,
            "<UNK>": 1,
            "<NUM>": 2,
        }

        num_special_tokens = len(vocab_mapping)

        for i, word in enumerate(sorted(vocab)):
            vocab_mapping[word] = i + num_special_tokens

        with open(constants.VOCAB_MAPPING_FILE_PATH, "w") as f:
            json.dump(vocab_mapping, f, indent=4)

        return vocab_mapping

    return (get_vocab_mapping,)


@app.cell
def _(get_vocab_mapping):
    vocab_mapping = get_vocab_mapping()
    vocab_mapping
    return (vocab_mapping,)


@app.cell
def _(NDArray, constants, glove_file_contents, np, random, vocab_mapping):
    EXPECTED_GLOVE_EMBEDDING_LENGTH = 100

    def get_matrix_embeddings() -> NDArray[np.float32]:
        random.seed(42)

        vectors = [[] for _ in range(len(vocab_mapping))]
        embedding_length = len(glove_file_contents[0].split(" ")[1:])

        assert embedding_length == EXPECTED_GLOVE_EMBEDDING_LENGTH

        vectors[0] = ["0.0"] * embedding_length
        vectors[1] = [str(random.uniform(-1, 1)) for _ in range(embedding_length)]
        vectors[2] = [str(random.uniform(-1, 1)) for _ in range(embedding_length)]

        for line in glove_file_contents:
            parts = line.split(" ")

            word = parts[0]

            if word not in vocab_mapping:
                continue

            embedding = parts[1:]

            vectors[vocab_mapping[word]] = embedding

        vectors = np.array(vectors, dtype=np.float32)

        np.save(constants.MATRIX_EMBEDDINGS_FILE_PATH, vectors)

        return vectors

    return (get_matrix_embeddings,)


@app.cell
def _(get_matrix_embeddings):
    vectors = get_matrix_embeddings()
    vectors
    return


if __name__ == "__main__":
    app.run()
