from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from config import Settings, get_settings
from database.models.accounts import (
    ActivationToken,
    PasswordResetToken,
    RefreshToken,
    User,
    UserGroup,
)
from database.models.enums import UserGroupEnum
from database.repositories.accounts import (
    ActivationTokenRepository,
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    UserGroupRepository,
    UserRepository,
)
from database.repositories.repository import SQLAlchemyRepository
from exceptions.accounts import (
    DefaultGroupNotFoundError,
    InvalidOrExpiredTokenError,
    UserAlreadyActivatedError,
    UserAlreadyExistsError,
)
from security.passwords import hash_password
from security.utils import generate_secure_token, hash_token
from services.base import BaseCRUDService


class AccountService(BaseCRUDService[User]):
    def __init__(self, session: AsyncSession, settings: Settings | None = None) -> None:
        super().__init__(session, UserRepository)
        self._settings = settings or get_settings()
        self._group_repo = UserGroupRepository(session)
        self._activation_token_repo = ActivationTokenRepository(session)
        self._password_token_repo = PasswordResetTokenRepository(session)
        self._refresh_token_repo = RefreshTokenRepository(session)

    async def register(self, email: str, password: str) -> tuple[User, str]:
        if await self._repo.get(User.email == email) is not None:
            raise UserAlreadyExistsError()

        default_group = await self._group_repo.get(UserGroup.name == UserGroupEnum.USER)
        if default_group is None:
            raise DefaultGroupNotFoundError()

        try:
            user = await self._repo.create(
                {
                    "email": email,
                    "hashed_password": hash_password(password),
                    "group_id": default_group.id,
                }
            )
        except IntegrityError as e:
            await self._session.rollback()
            raise UserAlreadyExistsError() from e

        raw_token = await self._issue_token(
            self._activation_token_repo,
            user.id,
            timedelta(hours=self._settings.ACTIVATION_TOKEN_TTL_HOURS),
            commit=False,
        )

        await self._session.commit()
        return user, raw_token

    async def activate_account(self, token: str) -> User:
        token_record = await self._activation_token_repo.get(
            ActivationToken.token_hash == hash_token(token)
        )
        if token_record is None:
            raise InvalidOrExpiredTokenError()

        expires_at = token_record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise InvalidOrExpiredTokenError()

        user = await self._repo.get(User.id == token_record.user_id)
        if user is None:
            raise InvalidOrExpiredTokenError()
        if user.is_active:
            raise UserAlreadyActivatedError()
        user.is_active = True

        await self._activation_token_repo.delete(ActivationToken.id == token_record.id)
        await self._session.commit()
        return user

    async def _issue_token(
        self,
        token_repo: SQLAlchemyRepository,
        user_id: int,
        ttl: timedelta,
        commit: bool = True,
    ) -> str:
        await token_repo.delete(token_repo.model.user_id == user_id)
        raw_token = generate_secure_token()
        await token_repo.create(
            {
                "user_id": user_id,
                "token_hash": hash_token(raw_token),
                "expires_at": datetime.now(timezone.utc) + ttl,
            }
        )
        if commit:
            await self._session.commit()
        return raw_token

    async def refresh_activation_token(self, email: str) -> str | None:
        user = await self._repo.get(User.email == email)
        if user is None or user.is_active:
            return None

        return await self._issue_token(
            self._activation_token_repo,
            user.id,
            timedelta(hours=self._settings.ACTIVATION_TOKEN_TTL_HOURS),
        )

    async def request_password_reset(self, email: str) -> str | None:
        user = await self._repo.get(User.email == email)
        if user is None or not user.is_active:
            return None

        return await self._issue_token(
            self._password_token_repo,
            user.id,
            timedelta(minutes=self._settings.PASSWORD_RESET_TOKEN_TTL_MINUTES),
        )

    async def confirm_password_reset(self, token: str, new_password: str) -> User:
        token_record = await self._password_token_repo.get(
            PasswordResetToken.token_hash == hash_token(token)
        )
        if token_record is None:
            raise InvalidOrExpiredTokenError()

        expires_at = token_record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            raise InvalidOrExpiredTokenError()

        user = await self._repo.get(User.id == token_record.user_id)
        if user is None or not user.is_active:
            raise InvalidOrExpiredTokenError()
        user.hashed_password = hash_password(new_password)

        await self._password_token_repo.delete(PasswordResetToken.id == token_record.id)
        await self._refresh_token_repo.delete(
            RefreshToken.user_id == token_record.user_id
        )
        await self._session.commit()
        return user
