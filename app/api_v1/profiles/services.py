from typing import Any, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.exceptions import CustomException
from app.api_v1.profiles.repository import ProfileRepository
from app.api_v1.profiles.schemas import ProfileCreate, ProfileShow, ProfileUpdate


class ProfileService:

    @staticmethod
    async def add_profile_user(profile_data: ProfileCreate, session: AsyncSession) -> int:
        try:
            if profile_data.user_id <= 0:
                raise CustomException(exception="inadmissible user_id").http_error_400
            profile_dict: dict[str, Any] = profile_data.model_dump()
            return await ProfileRepository(session=session).add_one(data=profile_dict)
        except IntegrityError:
            raise CustomException(exception="the profile already exists").http_error_400

    @staticmethod
    async def get_profiles_users(session: AsyncSession) -> list[ProfileShow]:
        return await ProfileRepository(session=session).find_all()

    @staticmethod
    async def get_profile_user(user_id: int, session: AsyncSession) -> ProfileShow:
        profile_user: Optional[ProfileShow] = await (ProfileRepository(session=session).
                                                     find_one_by_param(param_column="user_id",
                                                                       param_value=user_id))

        if profile_user:
            return profile_user
        raise CustomException(exception="profile not found").http_error_400

    @staticmethod
    async def delete_profile_user(user_id: int, session: AsyncSession) -> int:
        return await ProfileRepository(session=session).delete_one(id_data=user_id)

    @staticmethod
    async def update_profile(profile_id: int,
                             session: AsyncSession,
                             new_profile: ProfileUpdate) -> dict[str, Any]:
        new_profile: dict[str, Any] = new_profile.model_dump()
        return await ProfileRepository(session=session).update_one(id_data=profile_id,
                                                                   new_data=new_profile)


profile_service = ProfileService()
