from typing import Optional, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.exceptions import HttpAPIException
from app.api_v1.users.database import user_db
from app.api_v1.users.models import User


class UserValidator:
    """
    Класс для проверки данных пользователя
    """

    @staticmethod
    async def validate_user_data_by_field(session: AsyncSession,
                                          value: Any,
                                          field: str | tuple = "id") -> Optional[User]:
        error_message = "Данный пользователь уже зарегистрирован, выберите другой"

        if type(field) == str:
            return await user_db.get_user_by_field(session=session, column=field, value=value)

        for i in range(len(field)):
            existing_user: User | None = await user_db.get_user_by_field(session=session,
                                                                         column=field[i],
                                                                         value=value[i])
            if existing_user is not None:
                raise HttpAPIException(f"{error_message} {field[i]}.").http_error_400

        return None
