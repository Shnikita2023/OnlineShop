from typing import Any

from pydantic import EmailStr
from sqlalchemy import select, Result, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.exceptions import HttpAPIException
from app.api_v1.users import UserShow
from app.api_v1.users.models import User
from app.api_v1.users.schemas import UserCreate


class UserDatabase:
    error_bd = "Ошибка подключение к БД"

    @classmethod
    async def create_user(cls, session: AsyncSession, user_data: UserCreate) -> UserShow:
        user: User = User(**user_data.model_dump())
        try:
            session.add(user)
            await session.commit()
            return user.to_read_model()

        except ConnectionError:
            raise HttpAPIException(exception=cls.error_bd).http_error_500

    @classmethod
    async def get_user_by_field(cls, session: AsyncSession, column: str, value: Any):
        try:
            query = select(User).filter_by(**{column: value})
            result: Result = await session.execute(query)
            user: User | None = result.scalar_one_or_none()
            return user

        except ConnectionError:
            raise HttpAPIException(exception=cls.error_bd).http_error_500

    @classmethod
    async def get_user_by_email(cls, session: AsyncSession, email: EmailStr) -> User | None:
        try:
            query = select(User).where(User.email == email)
            result: Result = await session.execute(query)
            user: User | None = result.scalar_one_or_none()
            return user

        except ConnectionError:
            raise HttpAPIException(exception=cls.error_bd).http_error_500

    @classmethod
    async def get_user_by_id(cls, session: AsyncSession, user_id: int) -> User | None:
        try:
            user: User | None = await session.get(User, user_id)
            return user

        except ConnectionError:
            raise HttpAPIException(exception=cls.error_bd).http_error_500

    @classmethod
    async def get_emails_users(cls, session: AsyncSession) -> list:
        try:
            query = select(User.email)
            result: Result = await session.execute(query)
            emails_users = result.scalars().all()
            return list(emails_users)

        except ConnectionError:
            raise HttpAPIException(exception=cls.error_bd).http_error_500

    @classmethod
    async def update_partially_data_user(cls,
                                         session: AsyncSession,
                                         id_data: int,
                                         new_data: Any):
        try:
            stmt = update(User).where(User.id == id_data).values(new_data)
            await session.execute(stmt)
            await session.commit()
            return new_data

        except ConnectionError:
            raise HttpAPIException(exception=cls.error_bd).http_error_500


user_db = UserDatabase()
