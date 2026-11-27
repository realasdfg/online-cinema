from typing import Annotated

from fastapi import Depends

from dependencies.common import SessionDep, SettingsDep
from services.accounts import AccountService
from services.users import UserService


def get_account_service(session: SessionDep, settings: SettingsDep) -> AccountService:
    return AccountService(session=session, settings=settings)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]


def get_user_service(session: SessionDep) -> UserService:
    return UserService(session=session)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
