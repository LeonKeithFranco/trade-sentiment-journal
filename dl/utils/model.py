from dataclasses import dataclass, field
from functools import lru_cache
from typing import Literal

import numpy as np
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence

from utils import constants


@dataclass(slots=True)
class EpochResults:
    average_loss: float = 0.0
    predictions: list[int] = field(default_factory=list)
    actual: list[int] = field(default_factory=list)


class Model(nn.Module):
    def __init__(self, matrix_embedding: torch.Tensor) -> None:
        super().__init__()

        self.embedding = nn.Embedding.from_pretrained(
            matrix_embedding,
            freeze=True,
            padding_idx=0,
        )
        self.lstm = nn.LSTM(
            self.embedding.embedding_dim,
            hidden_size=128,
            batch_first=True,
            bidirectional=True,
        )
        self.linear1 = nn.Linear(
            self.lstm.hidden_size * 2,
            64,
        )
        self.linear2 = nn.Linear(
            self.linear1.out_features,
            3,
        )

        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

    def forward(self, sequences: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(sequences)

        _, (hn, _) = self.lstm(
            pack_padded_sequence(
                embedded, lengths, batch_first=True, enforce_sorted=False
            )
        )

        concatenated_hn = torch.concat((hn[0], hn[1]), dim=1)

        return self.linear2(
            self.dropout(
                self.relu(
                    self.linear1(concatenated_hn),
                ),
            ),
        )


@lru_cache
def _get_matrix_embedding() -> torch.Tensor:
    return torch.tensor(np.load(constants.MATRIX_EMBEDDINGS_FILE_PATH))


@lru_cache
def _load_trained_model() -> torch.nn.Module:
    model = Model(_get_matrix_embedding())
    model.load_state_dict(torch.load(constants.MODEL_FILE_PATH, weights_only=True))
    model.eval()

    return model


def get_model(type_: Literal["trained", "untrained"]) -> nn.Module:
    match type_:
        case "untrained":
            return Model(_get_matrix_embedding())
        case "trained":
            return _load_trained_model()
