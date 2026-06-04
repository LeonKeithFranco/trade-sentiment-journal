import asyncio
from functools import lru_cache

import torch
from dl.constants import CLASSES
from dl.model import get_model as get_dl_model
from torch import nn

from dl import constants


@lru_cache
def get_model() -> nn.Module:
    try:
        return get_dl_model()
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"{constants.MODEL_FILE_PATH} file could not be loaded; file may not yet exist"
        ) from exc


def _inference_runner(model: nn.Module, input: list[int]) -> tuple[str, float]:
    sequence = torch.tensor([input], dtype=torch.long)
    length = torch.tensor([len(input)], dtype=torch.long)

    with torch.inference_mode():
        logits = model(sequence, length)
        predictions = torch.softmax(logits, dim=-1)
        values, indices = predictions.max(dim=-1)

        index = int(indices.item())
        confidence = values.item()

    class_ = CLASSES[index]

    return class_, confidence


async def model_inference(input: list[int]) -> tuple[str, float]:
    return await asyncio.to_thread(
        _inference_runner,
        model=get_model(),
        input=input,
    )
