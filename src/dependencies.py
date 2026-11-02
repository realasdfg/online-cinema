from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from database.session import get_async_session
from notifications.emails import EmailSender
from notifications.interfaces import EmailSenderInterface
from security.tokens import JWTAuthManager
from services.accounts import AccountService
from services.auth import AuthService

SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


def get_jwt_auth_manager(settings: SettingsDep) -> JWTAuthManager:
    return JWTAuthManager(settings=settings)


JWTManagerDep = Annotated[JWTAuthManager, Depends(get_jwt_auth_manager)]


def get_account_service(session: SessionDep, settings: SettingsDep) -> AccountService:
    return AccountService(session=session, settings=settings)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]


def get_auth_service(session: SessionDep, jwt_manager: JWTManagerDep) -> AuthService:
    return AuthService(session=session, jwt_manager=jwt_manager)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_email_sender(settings: SettingsDep) -> EmailSenderInterface:
    return EmailSender(
        hostname=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        email=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        template_dir=settings.PATH_TO_EMAIL_TEMPLATES_DIR,
    )


EmailSenderDep = Annotated[EmailSenderInterface, Depends(get_email_sender)]
