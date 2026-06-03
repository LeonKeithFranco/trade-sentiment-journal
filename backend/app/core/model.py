import asyncio

from dl.model import get_model as get_dl_model
from torch import nn

from dl import constants


async def get_model() -> nn.Module:
    try:
        return await asyncio.to_thread(get_dl_model)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"{constants.MODEL_FILE_PATH} file could not be loaded; file may not yet exist"
        ) from exc
