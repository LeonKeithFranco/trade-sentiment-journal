import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell
def _():
    import datasets
    import torch
    from torch import nn
    from torch.utils.data import DataLoader
    from torch.optim import Optimizer
    from utils import constants
    from utils.get_dataset import get_dataset
    from utils.model import get_untrained_model, EpochResults
    from utils.preprocess import map_sentence
    from sklearn.metrics import confusion_matrix
    import copy

    return (
        DataLoader,
        EpochResults,
        Optimizer,
        confusion_matrix,
        constants,
        datasets,
        get_dataset,
        get_untrained_model,
        map_sentence,
        nn,
        torch,
    )


@app.cell
def _(torch):
    torch.manual_seed(42)
    return


@app.cell
def _():
    CLASSES = ["negative", "neutral", "positive"]
    return (CLASSES,)


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
    return train_dataloader, val_dataloader


@app.cell
def _(torch):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device
    return (device,)


@app.cell
def _(DataLoader, EpochResults, Optimizer, device, nn):
    def train_epoch(
        model: nn.Module,
        dataloader: DataLoader,
        criterion: nn.CrossEntropyLoss,
        optimizer: Optimizer,
    ) -> EpochResults:
        model.train()

        results = EpochResults()

        for sequence, labels, lengths in dataloader:
            sequence = sequence.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            logits = model(sequence, lengths)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()

            results.average_loss += loss.item()
            preds = logits.argmax(dim=1)
            results.predictions.extend(preds.cpu().tolist())
            results.actual.extend(labels.cpu().tolist())

        results.average_loss /= len(dataloader)

        return results

    return (train_epoch,)


@app.cell
def _(DataLoader, EpochResults, device, nn, torch):
    def validation_epoch(
        model: nn.Module, dataloader: DataLoader, criterion: nn.CrossEntropyLoss
    ) -> EpochResults:
        model.eval()

        results = EpochResults()

        with torch.no_grad():
            for sequence, labels, lengths in dataloader:
                sequence = sequence.to(device)
                labels = labels.to(device)

                logits = model(sequence, lengths)
                loss = criterion(logits, labels)

                results.average_loss += loss.item()
                preds = logits.argmax(dim=1)
                results.predictions.extend(preds.cpu().tolist())
                results.actual.extend(labels.cpu().tolist())

        results.average_loss /= len(dataloader)

        return results

    return (validation_epoch,)


@app.cell
def _(confusion_matrix):
    def print_metrics(
        predictions: list[int], labels: list[int], split: str
    ) -> None:
        print(f"===== {split} Confusion Matrix =====")
        print(confusion_matrix(labels, predictions))

    return (print_metrics,)


@app.cell
def _(CLASSES, device, torch, train_dataset):
    def compute_class_weights() -> torch.Tensor:
        num_classes = len(CLASSES)
        counts = torch.ones(num_classes)

        for _, label in train_dataset:
            counts[label] += 1

        weights = 1.0 / counts
        weights /= weights.sum() * num_classes

        return weights.to(device)

    return (compute_class_weights,)


@app.cell
def _(
    compute_class_weights,
    constants,
    device,
    get_untrained_model,
    nn,
    print_metrics,
    torch,
    train_dataloader,
    train_epoch,
    val_dataloader,
    validation_epoch,
):
    def train() -> None:
        num_epochs = 16
        model = get_untrained_model()

        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=1e-3,
        )
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            num_epochs,
            eta_min=1e-7,
        )
        criterion = nn.CrossEntropyLoss(
            weight=compute_class_weights(),
        )

        best_val_loss = float("inf")
        best_model_dict = {}

        model.to(device)

        for epoch in range(1, num_epochs + 1):
            train_results = train_epoch(
                model, train_dataloader, criterion, optimizer
            )
            scheduler.step()

            val_results = validation_epoch(model, val_dataloader, criterion)

            print(
                f"Epoch {epoch}/{num_epochs} |"
                f" train loss: {train_results.average_loss:.4f} |"
                f" val loss: {val_results.average_loss:.4f}"
            )
            print("\n")

            print_metrics(train_results.predictions, train_results.actual, "Train")
            print("\n")

            print_metrics(
                val_results.predictions, val_results.actual, "Validation"
            )
            print("\n")

            if val_results.average_loss < best_val_loss:
                best_val_loss = val_results.average_loss
                best_model_dict = {
                    k: v.cpu().clone() for k, v in model.state_dict().items()
                }

        torch.save(best_model_dict, constants.MODEL_FILE_PATH)

    return (train,)


@app.cell
def _(train):
    train()
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
