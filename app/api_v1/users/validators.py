from typing import Optional

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.users.database import user_db
from app.api_v1.users.models import User


class UserValidator:
    @staticmethod
    async def validate_user_data_by_email(user_email: EmailStr,
                                          session: AsyncSession) -> Optional[User]:
        existing_user: User | None = await user_db.get_user_by_email(session=session,
                                                                     email=user_email)
        return existing_user

    @staticmethod
    async def validate_user_data_by_id(user_id: int,
                                       session: AsyncSession) -> Optional[User]:
        existing_user: User | None = await user_db.get_user_by_id(session=session,
                                                                  user_id=user_id)
        return existing_user
