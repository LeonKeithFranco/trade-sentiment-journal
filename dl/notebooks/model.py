import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import torch
    from torch.utils.data import DataLoader
    from torch.nn.utils.rnn import pack_padded_sequence
    from torch import nn
    import datasets
    from utils.get_dataset import get_dataset
    from utils.preprocess import map_sentence
    import numpy as np
    from utils import constants

    return (
        DataLoader,
        constants,
        datasets,
        get_dataset,
        map_sentence,
        nn,
        np,
        pack_padded_sequence,
        torch,
    )


@app.cell
def _(get_dataset):
    full_dataset = get_dataset()
    full_dataset
    return (full_dataset,)


@app.cell
def _(datasets, map_sentence, torch):
    class SentenceDataset(torch.utils.data.Dataset):
        def __init__(self, dataset: datasets.arrow_dataset.Dataset) -> None:
            self.mapped_sentences: list[torch.Tensor] = [
                torch.tensor(map_sentence(data["sentence"]), dtype=torch.long)
                for data in dataset
            ]
            self.labels: list[torch.Tensor] = [
                torch.tensor(data["label"], dtype=torch.long) for data in dataset
            ]

        def __len__(self) -> int:
            return len(self.labels)

        def __getitem__(self, i: int) -> tuple[torch.Tensor, torch.Tensor]:
            return self.mapped_sentences[i], self.labels[i]

    return (SentenceDataset,)


@app.cell
def _(SentenceDataset, full_dataset):
    train_dataset = SentenceDataset(full_dataset["train"])
    train_dataset[0]
    return (train_dataset,)


@app.cell
def _(SentenceDataset, full_dataset):
    val_dataset = SentenceDataset(full_dataset["validation"])
    val_dataset[0]
    return (val_dataset,)


@app.cell
def _(SentenceDataset, full_dataset):
    test_dataset = SentenceDataset(full_dataset["test"])
    test_dataset[0]
    return (test_dataset,)


@app.cell
def _(torch):
    def collate(
        batch: list[tuple[torch.Tensor, torch.Tensor]],
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        max_length = max(len(data) for data, _ in batch)

        padded_batch = []
        labels = []
        true_length = []

        for data, label in batch:
            length = len(data)
            true_length.append(length)

            labels.append(label)

            padded_data = torch.zeros(max_length, dtype=torch.long)
            padded_data[:length] = data
            padded_batch.append(padded_data)

        return (
            torch.stack(padded_batch),
            torch.stack(labels),
            torch.tensor(true_length),
        )

    return (collate,)


@app.cell
def _(DataLoader, collate, train_dataset):
    train_dataloader = DataLoader(
        train_dataset, batch_size=32, shuffle=True, collate_fn=collate
    )
    sample_batch = next(iter(train_dataloader))
    sample_batch[0].shape, sample_batch[1].shape, sample_batch[2].shape
    return (sample_batch,)


@app.cell
def _(DataLoader, collate, test_dataset, val_dataset):
    val_dataloader = DataLoader(
        val_dataset, batch_size=32, shuffle=False, collate_fn=collate
    )
    test_dataloader = DataLoader(
        test_dataset, batch_size=32, shuffle=False, collate_fn=collate
    )
    return


@app.cell
def _(constants, np, torch):
    matrix_embedding = torch.tensor(np.load(constants.MATRIX_EMBEDDINGS_FILE_PATH))
    matrix_embedding
    return (matrix_embedding,)


@app.cell
def _(nn, pack_padded_sequence, torch):
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

        def forward(
            self, sequences: torch.Tensor, lengths: torch.Tensor
        ) -> torch.Tensor:
            embedded = self.embedding(sequences)

            _, (hn, _) = self.lstm(
                pack_padded_sequence(
                    embedded, lengths, batch_first=True, enforce_sorted=False
                )
            )

            concatenated_hn = torch.concat((hn[0], hn[1]), dim=1)

            return self.linear(concatenated_hn)

    return (Model,)


@app.cell
def _(Model, matrix_embedding, sample_batch):
    model = Model(matrix_embedding)
    test = model(sample_batch[0], sample_batch[2])
    test.shape
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
