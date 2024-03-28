from redis.asyncio.client import Redis
from starlette import status

from fastapi import APIRouter, Depends

from app.api_v1.auth import AuthUser
from . import OrderCreate, OrderItemCreate, OrderUpdate, OrderShow
from .services import order_service, order_item_service
from app.api_v1.exceptions import HttpAPIException
from ..depends.dependencies import UOWDep
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
                       uow: UOWDep,
                       redis_client: Redis = Depends(get_async_redis_client),
                       user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, str]:
    if order.user_id == user["sub"]:
        number_order: int = await order_service.create_order(uow=uow,
                                                             order_data=order,
                                                             redis_client=redis_client)
        return {
            "message": f"order created with {number_order} number successfully"
        }

    raise HttpAPIException(exception="access denied.").http_error_403


@router_order.get(path="/{order_id}",
                  summary="Получение заказа пользователя",
                  response_model=OrderShow)
async def get_order(order_id: int,
                    uow: UOWDep,
                    redis_client: Redis = Depends(get_async_redis_client),
                    user: dict = Depends(AuthUser.get_current_auth_user)) -> OrderShow:
    return await order_service.get_order(uow=uow,
                                         user_current=user,
                                         redis_client=redis_client,
                                         order_id=order_id)


@router_order.put(path="/{order_id}",
                  summary="Обновление заказа пользователя",
                  response_model=OrderUpdate)
async def update_order(order_id: int,
                       new_order: OrderUpdate,
                       uow: UOWDep,
                       user: dict = Depends(AuthUser.get_current_auth_user)) -> OrderUpdate:
    return await order_service.update_order(uow=uow,
                                            new_order=new_order,
                                            order_id=order_id,
                                            user_current=user)


@router_order.delete(path="/{order_id}",
                     summary="Удаление заказа пользователя",
                     status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int,
                       uow: UOWDep,
                       user: dict = Depends(AuthUser.get_current_auth_user)) -> None:
    await order_service.delete_order(uow=uow,
                                     order_id=order_id,
                                     user_current=user)
    return None


@router_order_item.post(path="/",
                        summary="Создание элементов заказа пользователя",
                        status_code=status.HTTP_201_CREATED)
async def create_order_item(order_item: OrderItemCreate,
                            uow: UOWDep,
                            redis_client: Redis = Depends(get_async_redis_client),
                            user: dict = Depends(AuthUser.get_current_auth_user)) -> dict[str, str]:
    number_order_item: int = await order_item_service.add_order_item(uow=uow,
                                                                     order_item_data=order_item,
                                                                     user_current=user,
                                                                     redis_client=redis_client)
    return {
        "message": f"element order created with {number_order_item} number successfully"
    }
