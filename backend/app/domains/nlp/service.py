from typing import Annotated

from fastapi import Depends


class NLPSerive:
    pass


NLPSeriveDependency = Annotated[NLPSerive, Depends(NLPSerive)]
