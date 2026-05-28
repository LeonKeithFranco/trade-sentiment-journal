import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    from datasets import load_dataset, load_from_disk
    from utils import constants

    return constants, load_dataset, load_from_disk


@app.cell
def _(constants, load_dataset, load_from_disk):
    if constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH.exists():
        dataset = load_from_disk(constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH)
    else:
        dataset = load_dataset("lmassaron/FinancialPhraseBank")
        dataset.save_to_disk(constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH)

    dataset
    return


if __name__ == "__main__":
    app.run()
