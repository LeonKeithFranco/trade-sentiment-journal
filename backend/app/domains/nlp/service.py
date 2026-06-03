from typing import Annotated

from fastapi import Depends


class NLPService:
    pass


NLPServiceDependency = Annotated[NLPService, Depends(NLPService)]
