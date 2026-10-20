from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from database.session import get_async_session
from services.accounts import AccountService


def get_account_service(
    session: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings),
) -> AccountService:
    return AccountService(session, settings)

