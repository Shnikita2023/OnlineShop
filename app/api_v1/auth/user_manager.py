from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.users.creators import user_creator
from app.api_v1.users.validators import UserValidator
from app.api_v1.users import UserShow
from app.api_v1.users.schemas import UserCreate


class UserManager:
    """
    Пользовательский менеджер для работы с пользователем
    """

    @staticmethod
    async def create(
            user_data: UserCreate,
            session: AsyncSession,
            background_tasks: BackgroundTasks) -> UserShow:
        await UserValidator.validate_user_data_by_field(session=session,
                                                        field=("email", "username"),
                                                        value=(user_data.email, user_data.username))

        return await user_creator.create_user(user_data, session, background_tasks)


user_manager = UserManager()
