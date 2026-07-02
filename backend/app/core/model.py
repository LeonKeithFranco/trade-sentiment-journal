import asyncio
from functools import lru_cache

import torch
from dl.constants import CLASSES
from dl.model import get_model as get_dl_model
from torch import nn

from dl import constants


@lru_cache
def get_model() -> nn.Module:
    """Load and return the cached trained sentiment classification model.

    Returns:
        nn.Module: The pre-trained BiLSTM sentiment classifier.

    Raises:
        FileNotFoundError: If the model weights file does not exist on disk.
    """
    try:
        return get_dl_model()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"{constants.MODEL_FILE_PATH} file could not be loaded; file may not yet exist"
        ) from exc


def _inference_runner(model: nn.Module, input_: list[int]) -> tuple[str, float]:
    """Run a single forward pass of the sentiment model on a tokenized sequence.

    Wraps the token sequence as a batch of one, runs it through the model, and converts
    the resultings logits into a predicted class label and confidence score.

    Args:
        model: The sentiment classification model to run inference with.
        input_: The tokenized input sequence, as a list of vocabulary indices.

    Returns:
        tuple: A tuple of (class_, confidence), where class_ is the predicted sentiment
        label from CLASSES and confidence is the model's softmax probability for that
        class.
    """
    sequence = torch.tensor([input_], dtype=torch.long)
    length = torch.tensor([len(input_)], dtype=torch.long)

    with torch.inference_mode():
        logits = model(sequence, length)
        predictions = torch.softmax(logits, dim=-1)
        values, indices = predictions.max(dim=-1)

        index = int(indices.item())
        confidence = values.item()

    class_ = CLASSES[index]

    return class_, confidence


async def model_inference(input_: list[int]) -> tuple[str, float]:
    """Run sentiment inference on a tokenized sequence without blocking the event loop.

    Delegates to the synchronouce inference runner in a separate thread.

    Args:
        input_: The tokenized input sequence, as a list of vocabulary indices.

    Returns:
       tuple: A tuple of (class_, confidence), where class_ is the predicted sentiment
       label from CLASSES and confidence is the model's softmax probability for that
       class.
    """
    return await asyncio.to_thread(
        _inference_runner,
        model=get_model(),
        input_=input_,
    )
