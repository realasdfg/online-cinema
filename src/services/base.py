from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories.repository import SQLAlchemyRepository, TModel


class BaseCRUDService:
    def __init__(
        self, session: AsyncSession, repo_class: type[SQLAlchemyRepository[TModel]]
    ):
        self._session = session
        self._repo = repo_class(session)

    async def create(self, data: dict):
        obj = await self._repo.create(data)
        await self._session.commit()
        return obj

    async def get_one_by_id(self, id_: int):
        return await self._repo.get(self._repo.model.id == id_)

    async def get_all(self, *conditions, order_by=None):
        return await self._repo.list_all(*conditions, order_by=order_by)

    async def update_by_id(self, id_: int, update_data: dict):
        obj = await self._repo.update(self._repo.model.id == id_, data=update_data)
        await self._session.commit()
        return obj

    async def delete_by_id(self, id_: int):
        result = await self._repo.delete(self._repo.model.id == id_)
        await self._session.commit()
        return result
