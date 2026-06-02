from functools import lru_cache

import numpy as np
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence

from utils import constants


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
        self.linear = nn.Linear(
            self.lstm.hidden_size * 2,
            3,
        )

    def forward(self, sequences: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        embedded = self.embedding(sequences)

        _, (hn, _) = self.lstm(
            pack_padded_sequence(
                embedded, lengths, batch_first=True, enforce_sorted=False
            )
        )

        concatenated_hn = torch.concat((hn[0], hn[1]), dim=1)

        return self.linear(concatenated_hn)


@lru_cache
def get_model() -> nn.Module:
    matrix_embedding = torch.tensor(np.load(constants.MATRIX_EMBEDDINGS_FILE_PATH))

    return Model(matrix_embedding)
