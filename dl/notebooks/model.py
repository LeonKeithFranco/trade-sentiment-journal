import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import torch
    import datasets
    from utils.get_dataset import get_dataset
    from utils.preprocess import map_sentence

    return datasets, get_dataset, map_sentence, torch


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
                torch.tensor(data["label"])  #
                for data in dataset
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
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
