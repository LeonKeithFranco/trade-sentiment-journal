import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    from datasets import load_dataset, load_from_disk
    from utils import constants
    from utils.preprocess import process_sentence

    return constants, load_dataset, load_from_disk, process_sentence


@app.cell
def _(process_sentence):
    from datasets.arrow_dataset import Dataset
    from datasets import DatasetDict


    def process_dataset_sentences(dataset: Dataset) -> Dataset:
        return dataset.map(
            lambda data: {"sentence": process_sentence(data["sentence"])}
        )


    def process_full_dataset_sentences(full_dataset: DatasetDict) -> DatasetDict:
        return DatasetDict(
            {
                split: process_dataset_sentences(data)
                for split, data in full_dataset.items()
            }
        )

    return (process_full_dataset_sentences,)


@app.cell
def _(constants, load_dataset, load_from_disk, process_full_dataset_sentences):
    if constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH.exists():
        full_dataset = load_from_disk(constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH)
    else:
        full_dataset = load_dataset("lmassaron/FinancialPhraseBank")
        full_dataset = process_full_dataset_sentences(full_dataset)
        full_dataset.save_to_disk(constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH)

    full_dataset
    return (full_dataset,)


@app.cell
def _(full_dataset):
    full_dataset['train'][100]['sentence']
    return


if __name__ == "__main__":
    app.run()
