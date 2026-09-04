from collections.abc import Sequence
from typing import Generic

from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.repository import SQLAlchemyRepository, TModel
from exceptions.base import EntityNotFoundError


class BaseCRUDService(Generic[TModel]):
    def __init__(
        self, session: AsyncSession, repo_class: type[SQLAlchemyRepository[TModel]]
    ):
        self._session = session
        self._repo = repo_class(session)

    async def create(self, data: dict) -> TModel:
        obj = await self._repo.create(data)
        await self._session.commit()
        return obj

    async def get_one_by_id(self, id_: int) -> TModel | None:
        return await self._repo.get(self._repo.model.id == id_)

    async def get_all(self, *conditions, order_by=None) -> Sequence[TModel]:
        return await self._repo.list_all(*conditions, order_by=order_by)

    async def update_by_id(self, id_: int, update_data: dict) -> TModel:
        obj = await self._repo.update(self._repo.model.id == id_, data=update_data)
        if obj is None:
            raise EntityNotFoundError(self._repo.model.__name__, id_)
        await self._session.commit()
        return obj

    async def delete_by_id(self, id_: int) -> None:
        deleted = await self._repo.delete(self._repo.model.id == id_)
        if not deleted:
            raise EntityNotFoundError(self._repo.model.__name__, id_)
        await self._session.commit()
