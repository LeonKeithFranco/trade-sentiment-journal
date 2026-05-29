from pathlib import Path

_DATA_FOLDER_PATH = Path(__file__).parent.parent / "data"

GLOVE_EMBEDDINGS_FILE_PATH = _DATA_FOLDER_PATH / "glove.6B.100d.txt"
FINANCIAL_PHRASE_BANK_FOLDER_PATH = _DATA_FOLDER_PATH / "financial_phrase_bank"
VOCAB_MAPPING_FILE_PATH = _DATA_FOLDER_PATH / "vocab_mapping.json"
