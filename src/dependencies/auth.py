from typing import Annotated

from fastapi import Depends

from dependencies.common import SessionDep, SettingsDep
from security.tokens import JWTAuthManager
from services.auth import AuthService


def get_jwt_auth_manager(settings: SettingsDep) -> JWTAuthManager:
    return JWTAuthManager(settings=settings)


JWTManagerDep = Annotated[JWTAuthManager, Depends(get_jwt_auth_manager)]


def get_auth_service(session: SessionDep, jwt_manager: JWTManagerDep) -> AuthService:
    return AuthService(session=session, jwt_manager=jwt_manager)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
