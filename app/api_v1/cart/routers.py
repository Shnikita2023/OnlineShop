from typing import Any

from starlette import status
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import CartCreate, CartItemCreate, CartItemShow, CartItemUpdate, CartItemUpdatePartial, CartShow
from app.db import get_async_session
from .services import cart_item_service, cart_service
from app.api_v1.auth import AuthUser
from ..exceptions import HttpAPIException

router_cart_item = APIRouter(
    prefix="/cart_items",
    tags=["CartItem"]
)

router_cart = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@router_cart_item.post(path="/",
                       summary="Создание позиции в корзине",
                       status_code=status.HTTP_201_CREATED)
async def create_cart_item(cart_item: CartItemCreate,
                           session: AsyncSession = Depends(get_async_session),
                           user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, str]:
    number_cart_items: int = await cart_item_service.add_cart_item(session=session,
                                                                   cart_item_data=cart_item,
                                                                   user_current=user)
    return {
        "message": f"element cart create with {number_cart_items} number successfully"
    }


@router_cart_item.get(path="/{cart_id}",
                      summary="Получение всех позиции в корзине пользователя",
                      response_model=list[CartItemShow])
async def get_cart_items(cart_id: int,
                         session: AsyncSession = Depends(get_async_session),
                         user: dict = Depends(AuthUser.get_current_auth_user)) -> list[CartItemShow]:
    return await cart_item_service.get_cart_items(session=session, user_current=user, cart_id=cart_id)


@router_cart_item.get(path="/{cart_item_id}",
                      summary="Получение позиции в корзине пользователя",
                      response_model=CartItemShow)
async def get_cart_item(cart_item_id: int,
                        session: AsyncSession = Depends(get_async_session),
                        user: dict = Depends(AuthUser.get_current_auth_user)) -> CartItemShow:
    return await cart_item_service.get_cart_item(session=session, user_current=user, cart_item_id=cart_item_id)


@router_cart_item.delete(path="/{cart_item_id}", summary="Удаление позиции в корзине")
async def delete_cart_item(cart_item_id: int,
                           session: AsyncSession = Depends(get_async_session),
                           user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, str]:
    number_cart_item: int = await cart_item_service.delete_cart_item(session=session,
                                                                     cart_item_id=cart_item_id,
                                                                     user_current=user)
    return {
        "message": f"element cart removed with {number_cart_item} number successfully"
    }


@router_cart_item.patch(path="/{cart_item_id}", summary="Частичное обновление позиции в корзине")
async def update_partial_cart_item(cart_item_id: int,
                                   new_cart_item: CartItemUpdatePartial,
                                   session: AsyncSession = Depends(get_async_session),
                                   user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, Any]:
    return await cart_item_service.update_partial_cart_item(session=session,
                                                            cart_item_id=cart_item_id,
                                                            cart_item_data=new_cart_item)


@router_cart_item.put(path="/{cart_item_id}", summary="Обновление позиции в корзине")
async def update_cart_item(cart_item_id: int,
                           new_cart_item: CartItemUpdate,
                           session: AsyncSession = Depends(get_async_session),
                           user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, Any]:
    return await cart_item_service.update_cart_item(session=session,
                                                    cart_item_id=cart_item_id,
                                                    cart_item_data=new_cart_item)


@router_cart.post(path="/",
                  summary="Создание корзины",
                  status_code=status.HTTP_201_CREATED)
async def create_cart(cart: CartCreate,
                      session: AsyncSession = Depends(get_async_session),
                      user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, str]:
    if cart.user_id == user["sub"]:
        number_cart: int = await cart_service.add_cart(session=session,
                                                       cart_data=cart)
        return {
            "message": f"cart created with {number_cart} number successfully"
        }
    raise HttpAPIException(exception="access denied.").http_error_403


@router_cart.get(path="/{cart_id}",
                 summary="Получение корзины",
                 response_model=CartShow)
async def get_cart(cart_id: int,
                   session: AsyncSession = Depends(get_async_session),
                   user: dict = Depends(AuthUser.get_current_auth_user)) -> CartShow:
    cart_user: CartShow = await cart_service.get_cart(session=session, cart_id=cart_id)
    if cart_user.user_id == user["sub"]:
        return cart_user
    raise HttpAPIException(exception="access denied.").http_error_403


@router_cart.get(path="/",
                 summary="Получение корзины по параметрам индетификатора пользователя",
                 response_model=CartShow)
async def get_cart_by_param(user_id: int,
                            session: AsyncSession = Depends(get_async_session)) -> CartShow:
    # user: dict = Depends(AuthUser.get_current_auth_user)
    # if user["sub"] == user_id:
    return await cart_service.get_cart_by_param(session=session,
                                                value_cart=user_id,
                                                name_column="user_id")
    #
    # raise CustomException(exception="access denied.").http_error_403


@router_cart.delete(path="/{user_id}", summary="Удаление корзины")
async def delete_cart(user_id: int,
                      session: AsyncSession = Depends(get_async_session),
                      user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, str]:
    if user_id == user["sub"]:
        number_cart: int = await cart_service.delete_cart(session=session,
                                                          user_id=user_id)
        return {
            "message": f"cart removed with {number_cart} number successfully"
        }
    raise HttpAPIException(exception="access denied.").http_error_403
