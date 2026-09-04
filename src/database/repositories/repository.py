from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

TModel = TypeVar("TModel")


class AbstractRepository(ABC, Generic[TModel]):
    @abstractmethod
    async def create(self, data: dict) -> TModel:
        raise NotImplementedError

    @abstractmethod
    async def get(self, filters: dict) -> TModel | None:
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
