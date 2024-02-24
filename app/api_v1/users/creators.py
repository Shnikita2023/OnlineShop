from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.auth.password_service import password_service
from app.api_v1.users import UserShow
from app.api_v1.users.database import user_db
from app.api_v1.users.schemas import UserCreate
from app.api_v1.utils.send_letter_on_email import send_letter_on_after_register
from app.logging_config import MyLogger

logger = MyLogger(pathname=__name__).init_logger


class UserCreator:
    """
    Класс для создания пользователя
    """

    async def create_user(self,
                          user_data: UserCreate,
                          session: AsyncSession,
                          background_tasks: BackgroundTasks) -> UserShow:
        hashed_password: bytes = password_service.hash_password(password=user_data.password)
        user_data.password = hashed_password

        created_user = await user_db.create_user(session=session, user_data=user_data)
        background_tasks.add_task(self._on_after_register, created_user)
        logger.info(f"Пользователь {created_user.username} с id {created_user.id} успешно создан. Status: 201")
        return created_user

    @staticmethod
    async def _on_after_register(user: UserShow) -> None:
        await send_letter_on_after_register(email=user.email)


user_creator = UserCreator()
