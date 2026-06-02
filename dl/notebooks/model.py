import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import datasets
    import torch
    from torch.utils.data import DataLoader
    from utils.get_dataset import get_dataset
    from utils.model import get_model
    from utils.preprocess import map_sentence

    return DataLoader, datasets, get_dataset, get_model, map_sentence, torch


@app.cell
def _(get_dataset):
    full_dataset = get_dataset()
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
    val_dataset = SentenceDataset(full_dataset["validation"])
    test_dataset = SentenceDataset(full_dataset["test"])
    return test_dataset, train_dataset, val_dataset


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
def _(DataLoader, collate, test_dataset, train_dataset, val_dataset):
    train_dataloader = DataLoader(
        train_dataset, batch_size=32, shuffle=True, collate_fn=collate
    )
    val_dataloader = DataLoader(
        val_dataset, batch_size=32, shuffle=False, collate_fn=collate
    )
    test_dataloader = DataLoader(
        test_dataset, batch_size=32, shuffle=False, collate_fn=collate
    )
    return


@app.cell
def _(get_model):
    model = get_model()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
