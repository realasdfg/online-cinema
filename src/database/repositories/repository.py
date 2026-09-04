from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

TModel = TypeVar("TModel")


class AbstractRepository(ABC, Generic[TModel]):
    @abstractmethod
    async def create(self, data: dict) -> TModel:
        raise NotImplementedError

    @abstractmethod
    async def get(self, *conditions) -> TModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self, *conditions, order_by=None) -> Sequence[TModel]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, *conditions, data: dict) -> TModel | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, *conditions) -> bool:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository[TModel], Generic[TModel]):
    model: type[TModel]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict) -> TModel:
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.scalar_one()

    async def get(self, *conditions) -> TModel | None:
        stmt = select(self.model).where(*conditions)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_all(self, *conditions, order_by=None) -> Sequence[TModel]:
        stmt = select(self.model)
        if conditions:
            stmt = stmt.where(*conditions)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def update(self, *conditions, data: dict) -> TModel | None:
        stmt = (
            update(self.model).where(*conditions).values(**data).returning(self.model)
        )
        res = await self.session.execute(stmt)
        await self.session.flush()
        return res.scalar_one_or_none()

    async def delete(self, *conditions) -> bool:
        stmt = delete(self.model).where(*conditions)
        res = await self.session.execute(stmt)
        return res.rowcount > 0
