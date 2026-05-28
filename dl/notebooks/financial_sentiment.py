import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    from datasets import load_dataset, load_from_disk
    from utils import constants
    from utils.preprocess import process_full_dataset_sentences

    return (
        constants,
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
def _(full_dataset):
    full_dataset["train"][100]["sentence"]
    return


if __name__ == "__main__":
    app.run()
