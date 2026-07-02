from dataclasses import dataclass, field
from functools import lru_cache
from typing import Literal

import numpy as np
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence

from dl import constants


@dataclass(slots=True)
class EpochResults:
    """Aggregated results from a single training or evaluation epoch."""

    average_loss: float = 0.0
    predictions: list[int] = field(default_factory=list)
    actual: list[int] = field(default_factory=list)


class Model(nn.Module):
    """A bidirectional LSTM sentiment classifier over pre-trained word embeddings.

    Embeds a tokenized sentence using a frozen pre-trained embedding matrix,
    encodes it with a bidirectional LSTM, and classifies the concatenated
    final hidden states into one of three sentiment classes through a small
    feed-forward head.
    """

    def __init__(self, matrix_embedding: torch.Tensor) -> None:
        """Initialize the model's layers from a pre-trained embedding matrix.

        Args:
            matrix_embedding: The pre-trained word embedding matrix, with one
                row per vocabulary entry. Used to initialize a frozen
                embedding layer.
        """
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
        """Run a forward pass, producing per-class logits for a batch of sequences.

        Args:
            sequences: A batch of tokenized, padded input sequences, shaped
                (batch_size, max_sequence_length).
            lengths: The true (unpadded) length of each sequence in the
                batch.

        Returns:
            torch.Tensor: The raw per-class logits, shaped
                (batch_size, num_classes).
        """
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
    """Load and cache the pre-computed word embedding matrix from disk.

    Returns:
        torch.Tensor: The word embedding matrix, with one row per
            vocabulary entry.
    """
    return torch.tensor(np.load(constants.MATRIX_EMBEDDINGS_FILE_PATH))


@lru_cache
def _load_trained_model() -> torch.nn.Module:
    """Load and cache the trained model with its saved weights, in evaluation mode.

    Returns:
        torch.nn.Module: The trained Model instance, with weights loaded
            from disk and set to evaluation mode.
    """
    model = Model(_get_matrix_embedding())
    model.load_state_dict(torch.load(constants.MODEL_FILE_PATH, weights_only=True))
    model.eval()

    return model


def get_model(type_: Literal["trained", "untrained"] = "trained") -> nn.Module:
    """Return a Model instance, either freshly initialized or pre-trained.

    Args:
        type_: "trained" to load the saved model weights, or "untrained" to
            return a freshly initialized model with only the embedding
            layer populated. Defaults to "trained".

    Returns:
        nn.Module: The requested Model instance.
    """
    match type_:
        case "untrained":
            return Model(_get_matrix_embedding())
        case "trained":
            return _load_trained_model()
