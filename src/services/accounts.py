from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.accounts import ActivationToken, User, UserGroup
from database.models.enums import UserGroupEnum
from database.repositories.accounts import (
    ActivationTokenRepository,
    UserGroupRepository,
    UserRepository,
)
from exceptions.accounts import DefaultGroupNotFoundError, UserAlreadyExistsError
from security.passwords import hash_password
from security.utils import generate_secure_token, hash_token
from services.base import BaseCRUDService


class AccountService(BaseCRUDService[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserRepository)
        self._group_repo = UserGroupRepository(session)
        self._activation_token_repo = ActivationTokenRepository(session)

    async def register(self, email: str, password: str) -> tuple[User, str]:
        if await self._repo.get(User.email == email) is not None:
            raise UserAlreadyExistsError(email)

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
            raise UserAlreadyExistsError(email) from e

        raw_token = generate_secure_token()
        await self._activation_token_repo.create(
            {
                "user_id": user.id,
                "token_hash": hash_token(raw_token),
            }
        )

        await self._session.commit()
        return user, raw_token
