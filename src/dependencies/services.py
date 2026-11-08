from typing import Annotated

from fastapi import Depends

from dependencies.common import SessionDep, SettingsDep
from services.accounts import AccountService


def get_account_service(session: SessionDep, settings: SettingsDep) -> AccountService:
    return AccountService(session=session, settings=settings)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
