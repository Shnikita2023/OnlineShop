from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.users.creators import UserCreator
from app.api_v1.users.validators import UserValidator
from app.api_v1.exceptions import CustomException
from app.api_v1.users import UserShow
from app.api_v1.users.models import User
from app.api_v1.users.schemas import UserCreate


class UserManager:

    async def create(
            self,
            user_data: UserCreate,
            session: AsyncSession) -> UserShow:
        existing_user: User | None = await UserValidator.validate_user_data_by_email(session=session,
                                                                                     user_email=user_data.email)
        if existing_user is not None:
            error_message = "Данный пользователь уже зарегистрирован, выберите другой email."
            raise CustomException(error_message).http_error_400
        return await UserCreator().create_user(user_data, session)


user_manager = UserManager()
