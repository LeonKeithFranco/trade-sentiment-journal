import asyncio

from dl.model import get_model as get_dl_model
from torch import nn


async def get_model() -> nn.Module:
    try:
        return await asyncio.to_thread(get_dl_model())
    except FileNotFoundError:
        raise FileNotFoundError("Model pth file could not be loaded")
