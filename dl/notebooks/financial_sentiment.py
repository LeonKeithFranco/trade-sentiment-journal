import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    from datasets import load_dataset, load_from_disk
    from utils import constants
    from utils.preprocess import process_full_dataset_sentences
    import itertools

    return (
        constants,
        itertools,
        load_dataset,
        load_from_disk,
        process_full_dataset_sentences,
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
def _(constants):
    from datasets.arrow_dataset import Dataset
    import json


    def map_vocab(dataset: Dataset) -> dict[str, int]:
        if constants.VOCAB_MAPPING_FILE_PATH.exists():
            with open(constants.VOCAB_MAPPING_FILE_PATH, "r") as f:
                return json.load(f)

        mapping = {
            "<PAD>": 0,
            "<UNK>": 1,
            "<NUM>": 2,
        }

        index_tracker = 3

        for data in dataset:
            for word in data["sentence"].split(" "):
                if mapping.get(word):
                    continue

                mapping[word] = index_tracker
                index_tracker += 1

        with open(constants.VOCAB_MAPPING_FILE_PATH, "w") as f:
            json.dump(mapping, f, indent=2)

        return mapping

    return json, map_vocab


@app.cell
def _(full_dataset, map_vocab):
    mapping = map_vocab(full_dataset["train"])
    mapping
    return (mapping,)


@app.cell
def _(constants, json):
    def parse_glove_embeddings(
        vocab_mapping: dict[str, int],
    ) -> dict[str, list[float]]:
        if constants.GLOVE_EMBEDDINGS_PARSED_FILE_PATH.exists():
            with open(constants.GLOVE_EMBEDDINGS_PARSED_FILE_PATH, "r") as f:
                return json.load(f)

        embeddings = {}

        with open(constants.GLOVE_EMBEDDINGS_FILE_PATH, "r") as f:
            for idx, line in enumerate(f):
                if idx % 1000 == 0:
                    print(f"{idx} lines processed")

                parts = line.split(" ")

                word = parts[0]
                if vocab_mapping.get(word, None) is None:
                    continue

                dimensions = parts[1:]

                embeddings[word] = [float(dim) for dim in dimensions]

        with open(constants.GLOVE_EMBEDDINGS_PARSED_FILE_PATH, "w") as f:
            json.dump(embeddings, f, indent=2)

        return embeddings

    return (parse_glove_embeddings,)


@app.cell
def _(itertools, mapping, parse_glove_embeddings):
    glove_embeddings = parse_glove_embeddings(mapping)
    dict(itertools.islice(glove_embeddings.items(), 5))
    return (glove_embeddings,)


@app.cell
def _(glove_embeddings):
    glove_embeddings.get('the', None)
    return


@app.cell
def _(constants, json):
    import random


    def create_embeddings_matrix(
        vocab_mapping: dict[str, int],
        glove_embeddings: dict[str, list[float]],
    ) -> dict[int, list[float]]:
        if constants.MATRIX_EMBEDDINGS_FILE_PATH.exists():
            with open(constants.MATRIX_EMBEDDINGS_FILE_PATH, "r") as f:
                return json.load(f)

        random.seed(42)

        matrix = {
            0: [0.0] * 100,
            1: [random.uniform(-1, 1) for _ in range(100)],
            2: [random.uniform(-1, 1) for _ in range(100)],
        }

        for vocab, idx in vocab_mapping.items():
            if vocab.startswith("<") and vocab.endswith(">"):
                continue

            if vocab in glove_embeddings:
                matrix[idx] = glove_embeddings[vocab]

        with open(constants.MATRIX_EMBEDDINGS_FILE_PATH, "w") as f:
            json.dump(matrix, f, indent=2)

        return matrix

    return (create_embeddings_matrix,)


@app.cell
def _(create_embeddings_matrix, glove_embeddings, itertools, mapping):
    matrix_embeddings = create_embeddings_matrix(mapping, glove_embeddings)
    dict(itertools.islice(matrix_embeddings.items(), 5))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
