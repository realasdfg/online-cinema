from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from database.models.accounts import User
from database.models.enums import UserGroupEnum
from database.repositories.accounts import UserRepository
from dependencies.common import SessionDep, SettingsDep
from exceptions.auth import InvalidJWTError, PermissionDeniedError
from security.tokens import JWTAuthManager
from services.auth import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def get_jwt_auth_manager(settings: SettingsDep) -> JWTAuthManager:
    return JWTAuthManager(settings=settings)


JWTManagerDep = Annotated[JWTAuthManager, Depends(get_jwt_auth_manager)]


def get_auth_service(session: SessionDep, jwt_manager: JWTManagerDep) -> AuthService:
    return AuthService(session=session, jwt_manager=jwt_manager)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    jwt_manager: JWTManagerDep,
    session: SessionDep,
) -> User:
    if credentials is None:
        raise InvalidJWTError()

    payload = jwt_manager.decode_access_token(credentials.credentials)
    try:
        user_id = int(payload["sub"])
    except (KeyError, ValueError) as e:
        raise InvalidJWTError() from e

    user = await UserRepository(session).get(User.id == user_id)
    if user is None or not user.is_active:
        raise InvalidJWTError()
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def require_role(*allowed: UserGroupEnum):
    async def checker(user: CurrentUserDep) -> User:
        if user.group.name not in allowed:
            raise PermissionDeniedError()
        return user

    return checker


ModeratorDep = Annotated[User, Depends(require_role(UserGroupEnum.MODERATOR))]
AdminDep = Annotated[User, Depends(require_role(UserGroupEnum.ADMIN))]
StaffDep = Annotated[
    User, Depends(require_role(UserGroupEnum.ADMIN, UserGroupEnum.MODERATOR))
]
