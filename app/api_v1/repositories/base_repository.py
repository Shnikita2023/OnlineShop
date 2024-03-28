from abc import ABC, abstractmethod
from typing import Any, Optional

from sqlalchemy import insert, select, delete, update
from fastapi.encoders import jsonable_encoder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.exceptions import HttpAPIException


class AbstractRepository(ABC):
    @abstractmethod
    async def add_one(self, data):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, id_data):
        raise NotImplementedError

    @abstractmethod
    async def find_one_by_param(self, param_column, param_value):
        raise NotImplementedError

    @abstractmethod
    async def find_all_by_param(self, param_column, value):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id_data):
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, id_data, new_data):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None
    error_500_by_bd = "Ошибка подключение к БД"

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_one(self, data: dict) -> int:
        try:
            stmt = insert(self.model).values(**data).returning(self.model.id)
            result = await self.session.execute(stmt)
            return result.scalar_one()

        except ConnectionError:
            raise HttpAPIException(exception=self.error_500_by_bd).http_error_500

        except IntegrityError:
            raise HttpAPIException(exception="duplicate entry").http_error_400

    async def find_one_by_param(self, param_column: str, param_value: Any) -> Optional[dict]:
        try:
            query = select(self.model).filter_by(**{param_column: param_value})
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()
            return jsonable_encoder(model)

        except ConnectionError:
            raise HttpAPIException(exception=self.error_500_by_bd).http_error_500

    async def find_one(self, id_data: int) -> Optional[dict]:
        try:
            query = select(self.model).where(self.model.id == id_data)
            result = await self.session.execute(query)
            model = result.scalar_one_or_none()
            return jsonable_encoder(model)

        except ConnectionError:
            raise HttpAPIException(exception=self.error_500_by_bd).http_error_500

    async def find_all(self) -> list[dict[str, Any]]:
        try:
            query = select(self.model)
            result = await self.session.execute(query)
            list_models = [jsonable_encoder(model[0]) for model in result.all()]
            return list_models

        except ConnectionError:
            raise HttpAPIException(exception=self.error_500_by_bd).http_error_500

    async def find_all_by_param(self, param_column: str, param_value: Any) -> list[dict[str, Any]]:
        try:
            query = select(self.model).filter_by(**{param_column: param_value})
            result = await self.session.execute(query)
            list_models = [jsonable_encoder(model[0]) for model in result.all()]
            return list_models

        except ConnectionError:
            raise HttpAPIException(exception=self.error_500_by_bd).http_error_500

    async def find_all_greater_than(self, param_column: str, param_value: Any) -> list[model]:
        try:
            column = getattr(self.model, param_column)
            query = select(self.model).where(column > param_value)
            result = await self.session.execute(query)
            list_models = list(result.scalars().all())
            return list_models

        except ConnectionError:
            raise HttpAPIException(exception=self.error_500_by_bd).http_error_500

    async def delete_one(self, id_data: int) -> int:
        try:
            find_id = await self.session.get(self.model, id_data)

            if find_id:
                stmt = delete(self.model).where(self.model.id == id_data).returning(self.model.id)
                result = await self.session.execute(stmt)
                return result.scalar_one()

            raise HttpAPIException(exception="id is not found").http_error_400

        except ConnectionError:
            raise HttpAPIException(exception=self.error_500_by_bd).http_error_500

    async def update_one(self, id_data: int, new_data: dict[str, Any]) -> dict[str, Any]:
        try:
            find_id = await self.session.get(self.model, id_data)

            if find_id:
                stmt = update(self.model).where(self.model.id == id_data).values(new_data)
                await self.session.execute(stmt)
                return new_data

            raise HttpAPIException(exception="id is not found").http_error_400

        except ConnectionError:
            raise HttpAPIException(exception=self.error_500_by_bd).http_error_500
