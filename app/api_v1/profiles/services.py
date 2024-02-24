from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.exceptions import HttpAPIException
from app.api_v1.profiles.repository import ProfileRepository
from app.api_v1.profiles.schemas import ProfileCreate, ProfileShow, ProfileUpdate


class ProfileService:
    """
    Сервис профиля
    """

    @staticmethod
    async def add_profile_user(profile_data: ProfileCreate, session: AsyncSession) -> int:
        """Добавление профиля пользователя"""

        if profile_data.user_id <= 0:
            raise HttpAPIException(exception="the user_id should be more 0").http_error_400

        profile_dict: dict[str, Any] = profile_data.model_dump()
        return await ProfileRepository(session=session).add_one(data=profile_dict)

    @staticmethod
    async def get_profiles_users(session: AsyncSession) -> list[ProfileShow]:
        """Получение всех профилей пользователя"""
        profiles_users: list[dict[str, Any]] = await ProfileRepository(session=session).find_all()
        schemas_profiles: list[ProfileShow] = [ProfileShow(**data) for data in profiles_users]
        return schemas_profiles

    @staticmethod
    async def get_profile_user(user_id: int, session: AsyncSession) -> ProfileShow:
        """Получение профиля пользователя"""
        profile_user: Optional[dict] = await (ProfileRepository(session=session).
                                              find_one_by_param(param_column="user_id",
                                                                param_value=user_id))
        if profile_user:
            return ProfileShow(**profile_user)

        raise HttpAPIException(exception="the profile not found").http_error_400

    @staticmethod
    async def delete_profile_user(user_id: int, session: AsyncSession) -> int:
        """Удаление профиля пользователя"""
        profile_user: ProfileShow = await profile_service.get_profile_user(user_id=user_id, session=session)
        return await ProfileRepository(session=session).delete_one(id_data=profile_user.id)

    @staticmethod
    async def update_profile(profile_id: int,
                             session: AsyncSession,
                             new_profile: ProfileUpdate) -> ProfileUpdate:
        """Обновление профиля пользователя"""
        new_profile: dict[str, Any] = new_profile.model_dump()
        update_profile_user: dict[str, Any] = await ProfileRepository(session=session).update_one(id_data=profile_id,
                                                                                                  new_data=new_profile)
        return ProfileUpdate(**update_profile_user)


profile_service = ProfileService()
