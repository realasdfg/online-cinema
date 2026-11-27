from sqlalchemy.ext.asyncio import AsyncSession

from database.models.accounts import RefreshToken, User, UserGroup
from database.models.enums import UserGroupEnum
from database.repositories.accounts import (
    RefreshTokenRepository,
    UserGroupRepository,
    UserRepository,
)
from exceptions.base import EntityNotFoundError
from exceptions.users import CannotChangeOwnGroupError
from services.base import BaseService


class UserService(BaseService[User]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserRepository)
        self._group_repo = UserGroupRepository(session)
        self._refresh_token_repo = RefreshTokenRepository(session)

    async def change_group(
        self, admin: User, user_id: int, new_group: UserGroupEnum
    ) -> User:
        user = await self._repo.get(User.id == user_id)
        if user is None:
            raise EntityNotFoundError("User", user_id)
        if user.id == admin.id:
            raise CannotChangeOwnGroupError()

        group = await self._group_repo.get(UserGroup.name == new_group)
        if group is None:
            raise EntityNotFoundError("UserGroup", new_group.value)

        user.group_id = group.id
        await self._refresh_token_repo.delete(RefreshToken.user_id == user.id)
        await self._session.commit()
        await self._session.refresh(user)
        return user
