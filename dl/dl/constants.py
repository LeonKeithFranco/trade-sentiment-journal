from pathlib import Path

_DATA_FOLDER_PATH = Path(__file__).parent.parent / "data"

GLOVE_EMBEDDINGS_ZIP_DOWNLOAD_LINK = (
    "https://huggingface.co/stanfordnlp/glove/resolve/main/glove.6B.zip"
)
GLOVE_EMBEDDINGS_ZIP_TARGET_MEMBER_FILE = "glove.6B.100d.txt"
GLOVE_EMBEDDINGS_FILE_PATH = _DATA_FOLDER_PATH / GLOVE_EMBEDDINGS_ZIP_TARGET_MEMBER_FILE
GLOVE_EMBEDDINGS_PARSED_FILE_PATH = _DATA_FOLDER_PATH / "glove_embeddings_parsed.json"
FINANCIAL_PHRASE_BANK_FOLDER_PATH = _DATA_FOLDER_PATH / "financial_phrase_bank"
VOCAB_MAPPING_FILE_PATH = _DATA_FOLDER_PATH / "vocab_mapping.json"
MATRIX_EMBEDDINGS_FILE_PATH = _DATA_FOLDER_PATH / "matrix_embeddings.npy"
MODEL_FILE_PATH = _DATA_FOLDER_PATH / "model.pth"

CLASSES = ["negative", "neutral", "positive"]
