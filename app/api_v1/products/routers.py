from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi_cache.decorator import cache
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.auth import AuthUser
from app.api_v1.exceptions import HttpAPIException
from app.api_v1.products.schemas import ProductShow, ProductCreate, ProductUpdate
from app.api_v1.products.services import product_service
from app.db import get_async_session

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get(path="/{product_id}",
            summary='Получение продукта',
            response_model=ProductShow
            )
async def get_product(product_id: int,
                      session: AsyncSession = Depends(get_async_session)) -> ProductShow:
    return await product_service.get_product(id_product=product_id, session=session)


@router.get(path="/",
            summary='Получение продукта по параметрам'
            )
async def get_product_by_product(product_value: Any,
                                 param_colum_product: str = "name",
                                 session: AsyncSession = Depends(get_async_session)) -> ProductShow:
    return await product_service.get_product_by_param(session=session,
                                                      param_colum_product=param_colum_product,
                                                      product_value=product_value)


@router.get(path="/all/",
            summary='Получение всех продуктов',
            response_model=list[ProductShow]
            )
@cache(expire=60)
async def get_products(session: AsyncSession = Depends(get_async_session)) -> list[ProductShow]:
    return await product_service.get_products(session=session)


@router.post(path="/",
             summary='Cоздание продукта',
             status_code=status.HTTP_201_CREATED
             )
async def create_product(product_data: ProductCreate,
                         session: AsyncSession = Depends(get_async_session),
                         user: dict = Depends(AuthUser.get_current_auth_user)) -> dict:

    if user["is_superuser"] is True:
        number_product: int = await product_service.add_product(session=session, product_data=product_data)

        return {
            "message": f"Product creates with {number_product} number successfully",
            "data": product_data
        }

    raise HttpAPIException(exception="access denied.").http_error_403


@router.delete(path="/{product_id}",
               summary='Удаление продукта',
               status_code=status.HTTP_204_NO_CONTENT
               )
async def delete_product(
        product_id: int,
        session: AsyncSession = Depends(get_async_session),
        user: dict = Depends(AuthUser.get_current_auth_user)) -> None:

    if user["is_superuser"] is True:
        await product_service.delete_product(id_product=product_id, session=session)

        return None

    raise HttpAPIException(exception="access denied.").http_error_403


@router.put(path="/{product_id}",
            summary='Обновление продукта'
            )
async def update_product(
        product_id: int,
        product_update: ProductUpdate,
        session: AsyncSession = Depends(get_async_session),
        user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, Any]:

    if user["is_superuser"] is True:
        return await product_service.update_product(id_product=product_id,
                                                    session=session,
                                                    new_product=product_update)

    raise HttpAPIException(exception="access denied.").http_error_403
