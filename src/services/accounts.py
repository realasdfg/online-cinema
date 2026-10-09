from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.accounts import User, UserGroup
from database.models.enums import UserGroupEnum
from database.repositories.accounts import UserGroupRepository, UserRepository
from exceptions.accounts import DefaultGroupNotFoundError, UserAlreadyExistsError
from security.passwords import hash_password
from services.base import BaseCRUDService


class AccountService(BaseCRUDService[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserRepository)
        self._group_repo = UserGroupRepository(session)

    async def register(self, email, password) -> User:
        if await self._repo.get(User.email == email) is not None:
            raise UserAlreadyExistsError(email)

        default_group = await self._group_repo.get(UserGroup.name == UserGroupEnum.USER)
        if default_group is None:
            raise DefaultGroupNotFoundError

        try:
            user = await self._repo.create(
                {
                    "email": email,
                    "hashed_password": hash_password(password),
                    "group_id": default_group.id,
                }
            )
            await self._session.commit()
        except IntegrityError as e:
            await self._session.rollback()
            raise UserAlreadyExistsError(email) from e
        return user
