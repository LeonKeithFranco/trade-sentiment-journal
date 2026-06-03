from typing import cast

from datasets.dataset_dict import DatasetDict
from datasets.load import load_dataset, load_from_disk

from dl import constants
from dl.preprocess import process_full_dataset_sentences

DATASET_NAME = "lmassaron/FinancialPhraseBank"


def get_dataset() -> DatasetDict:
    if constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH.exists():
        full_dataset = load_from_disk(constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH)
    else:
        full_dataset = load_dataset(DATASET_NAME)
        full_dataset = process_full_dataset_sentences(full_dataset)
        full_dataset.save_to_disk(constants.FINANCIAL_PHRASE_BANK_FOLDER_PATH)

    return cast(DatasetDict, full_dataset)
