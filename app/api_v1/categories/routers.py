from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache

from app.api_v1.auth.user_auth import AuthUser
from app.api_v1.categories import CategoryShow, CategoryCreate, CategoryUpdate
from app.api_v1.categories.services import category_service
from app.api_v1.depends.dependencies import UOWDep
from app.api_v1.exceptions import HttpAPIException

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get(path="/{category_id}",
            summary='Получение категории',
            response_model=CategoryShow
            )
async def get_category(category_id: int,
                       uow: UOWDep) -> CategoryShow:
    return await category_service.get_category(id_category=category_id, uow=uow)


@router.get(path="/",
            summary='Получение всех категории товаров',
            response_model=list[CategoryShow]
            )
@cache(expire=60)
async def get_categories(uow: UOWDep) -> list[CategoryShow]:
    return await category_service.get_categories(uow=uow)


@router.post(path="/",
             summary='Cоздание категории',
             status_code=status.HTTP_201_CREATED
             )
async def create_category(category_data: CategoryCreate,
                          uow: UOWDep,
                          user: dict = Depends(AuthUser.get_current_auth_user)) -> dict:
    if user["is_superuser"] is True:
        number_category: int = await category_service.add_category(uow=uow,
                                                                   category_data=category_data)
        return {
            "message": f"category creates with {number_category} number successfully",
            "data": category_data
        }

    raise HttpAPIException(exception="access denied.").http_error_403


@router.delete(path="/{category_id}",
               summary='Удаление категории',
               status_code=status.HTTP_204_NO_CONTENT
               )
async def delete_category(
        category_id: int,
        uow: UOWDep,
        user: dict = Depends(AuthUser.get_current_auth_user)) -> None:
    if user["is_superuser"] is True:
        await category_service.delete_category(id_category=category_id, uow=uow)
        return None

    raise HttpAPIException(exception="access denied.").http_error_403


@router.put(path="/{category_id}",
            summary='Обновление категории'
            )
async def update_category(
        category_id: int,
        category_update: CategoryUpdate,
        uow: UOWDep,
        user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, Any]:
    if user["is_superuser"] is True:
        return await category_service.update_category(id_category=category_id,
                                                      uow=uow,
                                                      new_category=category_update)

    raise HttpAPIException(exception="access denied.").http_error_403
