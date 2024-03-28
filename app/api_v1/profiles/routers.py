from fastapi import APIRouter, Depends, status

from app.api_v1.auth import AuthUser
from app.api_v1.depends.dependencies import UOWDep
from app.api_v1.exceptions import HttpAPIException
from app.api_v1.profiles.schemas import ProfileCreate, ProfileShow, ProfileUpdate
from app.api_v1.profiles.services import profile_service

router = APIRouter(
    prefix="/profiles",
    tags=["Profiles"]
)


@router.post(path="/",
             summary='Cоздание профиля',
             status_code=status.HTTP_201_CREATED,
             )
async def create_profile(profile_data: ProfileCreate,
                         uow: UOWDep,
                         user: dict = Depends(AuthUser.get_current_auth_user)) -> dict:
    if profile_data.user_id == user["sub"] or user["is_superuser"] is True:
        profile_user_id: int = await profile_service.add_profile_user(profile_data=profile_data,
                                                                      uow=uow)
        return {"message": f"the profile has been created successfully with number {profile_user_id}"}

    raise HttpAPIException(exception="access denied.").http_error_403


@router.delete(path='/{user_id}',
               summary="Удаление профиля",
               status_code=status.HTTP_204_NO_CONTENT
               )
async def delete_profile(user_id: int,
                         uow: UOWDep,
                         user: dict = Depends(AuthUser.get_current_auth_user)) -> None:
    if user_id == user["sub"] or user["is_superuser"] is True:
        await profile_service.delete_profile_user(user_id=user_id,
                                                  uow=uow)
        return None

    raise HttpAPIException(exception="access denied.").http_error_403


@router.get(path='/',
            summary="Получение всех профилей пользователей",
            response_model=list[ProfileShow]
            )
async def get_profiles(uow: UOWDep,
                       user: dict = Depends(AuthUser.get_current_auth_user)) -> list[ProfileShow]:
    if user["is_superuser"] is True:
        return await profile_service.get_profiles_users(uow=uow)

    raise HttpAPIException(exception="access denied.").http_error_403


@router.get(path='/{user_id}',
            summary="Получение профиля пользователя",
            response_model=ProfileShow
            )
async def get_profile(user_id: int,
                      uow: UOWDep,
                      user: dict = Depends(AuthUser.get_current_auth_user)) -> ProfileShow:
    if user_id == user["sub"] or user["is_superuser"] is True:
        return await profile_service.get_profile_user(user_id=user_id,
                                                      uow=uow)

    raise HttpAPIException(exception="access denied.").http_error_403


@router.put(path='/{profile_id}',
            summary="Обновление профиля",
            response_model=ProfileUpdate
            )
async def update_profile(profile_id: int,
                         profile_data: ProfileUpdate,
                         uow: UOWDep,
                         user: dict = Depends(AuthUser.get_current_auth_user)) -> ProfileUpdate:
    profile_user: ProfileShow = await profile_service.get_profile_user(user_id=user["sub"],
                                                                       uow=uow)

    if profile_user.id == profile_id or user["is_superuser"] is True:
        return await profile_service.update_profile(profile_id=profile_id,
                                                    uow=uow,
                                                    new_profile=profile_data)

    raise HttpAPIException(exception="access denied.").http_error_403
