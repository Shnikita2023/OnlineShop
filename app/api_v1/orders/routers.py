
from redis.asyncio.client import Redis
from starlette import status

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_async_session
from app.api_v1.auth import AuthUser
from . import OrderCreate, OrderItemCreate, OrderUpdate
from .services import order_service, order_item_service
from app.api_v1.exceptions import CustomException
from ...db.database import get_async_redis_client

router_order = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)

router_order_item = APIRouter(
    prefix="/order_items",
    tags=["OrderItems"]
)


@router_order.post(path="/",
                   summary="Создание заказа пользователя",
                   status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate,
                       session: AsyncSession = Depends(get_async_session),
                       redis_client: Redis = Depends(get_async_redis_client),
                       user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, str]:
    if order.user_id == user["sub"]:
        number_order: int = await order_service.add_order(session=session,
                                                          order_data=order,
                                                          redis_client=redis_client)
        return {
            "message": f"order created with {number_order} number successfully"
        }
    raise CustomException(exception="access denied.").http_error_403


@router_order.get(path="/{order_id}",
                  summary="Получение заказа пользователя")
async def get_order(order_id: int,
                    redis_client: Redis = Depends(get_async_redis_client),
                    session: AsyncSession = Depends(get_async_session),
                    user: dict = Depends(AuthUser.get_current_auth_user)):
    return await order_service.get_order(session=session,
                                         user_current=user,
                                         redis_client=redis_client,
                                         order_id=order_id)


@router_order.put(path="/{order_id}",
                  summary="Обновление заказа пользователя")
async def update_order(order_id: int,
                       new_order: OrderUpdate,
                       session: AsyncSession = Depends(get_async_session),
                       user: dict = Depends(AuthUser.get_current_auth_user)):
    return await order_service.update_order(session=session,
                                            new_order=new_order,
                                            order_id=order_id)


@router_order_item.post(path="/",
                        summary="Создание элементов заказа пользователя",
                        status_code=status.HTTP_201_CREATED)
async def create_order_item(order_item: OrderItemCreate,
                            session: AsyncSession = Depends(get_async_session),
                            redis_client: Redis = Depends(get_async_redis_client),
                            user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, str]:
    number_order_item: int = await order_item_service.add_order_item(session=session,
                                                                     order_item_data=order_item,
                                                                     user_current=user,
                                                                     redis_client=redis_client)
    return {
        "message": f"element order created with {number_order_item} number successfully"
    }
