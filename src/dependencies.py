from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from database.session import get_async_session
from notifications.emails import EmailSender
from notifications.interfaces import EmailSenderInterface
from security.tokens import JWTAuthManager
from services.accounts import AccountService
from services.auth import AuthService


def get_jwt_auth_manager(settings: Settings = Depends(get_settings)) -> JWTAuthManager:
    return JWTAuthManager(settings=settings)


def get_account_service(
    session: AsyncSession = Depends(get_async_session),
    settings: Settings = Depends(get_settings),
) -> AccountService:
    return AccountService(session=session, settings=settings)


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
    jwt_manager: JWTAuthManager = Depends(get_jwt_auth_manager),
) -> AuthService:
    return AuthService(session=session, jwt_manager=jwt_manager)


def get_email_sender(
    settings: Settings = Depends(get_settings),
) -> EmailSenderInterface:
    return EmailSender(
        hostname=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        email=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
        use_tls=settings.EMAIL_USE_TLS,
        template_dir=settings.PATH_TO_EMAIL_TEMPLATES_DIR,
    )
