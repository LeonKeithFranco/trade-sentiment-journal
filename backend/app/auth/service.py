from typing import Annotated

from fastapi import Depends


class AuthService:
    pass


AuthServiceDependency = Annotated[AuthService, Depends(AuthService)]
