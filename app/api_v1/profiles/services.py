from typing import Any, Optional

from app.api_v1.exceptions import HttpAPIException
from app.api_v1.profiles.schemas import ProfileCreate, ProfileShow, ProfileUpdate
from app.api_v1.utils.unitofwork import IUnitOfWork


class ProfileService:
    """
    Сервис профиля
    """

    @staticmethod
    async def add_profile_user(profile_data: ProfileCreate, uow: IUnitOfWork) -> int:
        """Добавление профиля пользователя"""

        if profile_data.user_id <= 0:
            raise HttpAPIException(exception="the user_id should be more 0").http_error_400

        profile_dict: dict[str, Any] = profile_data.model_dump()
        async with uow:
            profile_id: int = await uow.profile.add_one(data=profile_dict)
            await uow.commit()
            return profile_id

    @staticmethod
    async def get_profiles_users(uow: IUnitOfWork) -> list[ProfileShow]:
        """Получение всех профилей пользователя"""
        async with uow:
            profiles_users: list[dict[str, Any]] = await uow.profile.find_all()
            schemas_profiles: list[ProfileShow] = [ProfileShow(**data) for data in profiles_users]
            return schemas_profiles

    @staticmethod
    async def get_profile_user(user_id: int, uow: IUnitOfWork) -> ProfileShow:
        """Получение профиля пользователя"""
        async with uow:
            profile_user: Optional[dict] = await uow.profile.find_one_by_param(param_column="user_id",
                                                                               param_value=user_id)

            if profile_user:
                return ProfileShow(**profile_user)

            raise HttpAPIException(exception="the profile not found").http_error_400

    @staticmethod
    async def delete_profile_user(user_id: int, uow: IUnitOfWork) -> int:
        """Удаление профиля пользователя"""
        profile_user: ProfileShow = await profile_service.get_profile_user(user_id=user_id, uow=uow)
        async with uow:
            deleted_profile_id: int = await uow.profile.delete_one(id_data=profile_user.id)
            await uow.commit()
            return deleted_profile_id

    @staticmethod
    async def update_profile(profile_id: int,
                             uow: IUnitOfWork,
                             new_profile: ProfileUpdate) -> ProfileUpdate:
        """Обновление профиля пользователя"""
        new_profile: dict[str, Any] = new_profile.model_dump()
        async with uow:
            update_profile_user: dict[str, Any] = await uow.profile.update_one(id_data=profile_id,
                                                                               new_data=new_profile)
            await uow.commit()
            return ProfileUpdate(**update_profile_user)


profile_service = ProfileService()
