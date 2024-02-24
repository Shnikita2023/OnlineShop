from typing import Any, Optional

from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.exceptions import HttpAPIException
from app.api_v1.orders import OrderCreate, OrderItemCreate, OrderItemShow, OrderUpdate, OrderShow
from app.api_v1.orders.repository import OrderRepository, OrderItemRepository
from app.api_v1.products.services import product_service


class OrderService:

    @staticmethod
    async def check_existing_user_order(session: AsyncSession, user_current: dict, order_id: int) -> None:
        """Проверка существующего заказа и доступа пользователя"""
        order: Optional[dict] = await OrderRepository(session=session).find_one(id_data=order_id)

        if not order:
            raise HttpAPIException(exception="order not found").http_error_400

        if user_current["sub"] != order["user_id"]:
            raise HttpAPIException(exception="access denied").http_error_403

        return None

    @staticmethod
    async def create_order(order_data: OrderCreate, session: AsyncSession, redis_client: Redis) -> int:
        order_dict: dict[str, Any] = order_data.model_dump()
        order_id: int = await OrderRepository(session=session).add_one(data=order_dict)
        await redis_client.set(name=f"modified_order_{order_id}", value="False")

        return order_id

    @staticmethod
    async def get_order(session: AsyncSession,
                        redis_client: Redis,
                        user_current: dict,
                        order_id: int) -> OrderShow:

        await order_service.check_existing_user_order(session=session, user_current=user_current, order_id=order_id)

        is_modified_order_id: bool = await redis_client.get(f"modified_order_{order_id}")

        if is_modified_order_id:
            all_items_order: list[OrderItemShow] = await OrderItemService.get_order_items(session=session,
                                                                                          order_id=order_id)

            summa_total_price: float = sum(data.total_price for data in all_items_order)
            new_order = {"total_price": summa_total_price, "status": "Ready"}
            await OrderRepository(session=session).update_one(id_data=order_id, new_data=new_order)
            await redis_client.set(name=f"modified_order_{order_id}", value="False")

        order_user: Optional[dict] = await OrderRepository(session=session).find_one(id_data=order_id)

        return OrderShow(**order_user)

    @staticmethod
    async def update_order(session: AsyncSession,
                           order_id: int,
                           new_order: OrderUpdate,
                           user_current: dict) -> OrderUpdate:

        if user_current["sub"] != new_order.user_id:
            raise HttpAPIException(exception="access denied.").http_error_403

        order_dict: dict[str, Any] = new_order.model_dump()
        updated_order = await OrderRepository(session=session).update_one(id_data=order_id, new_data=order_dict)
        return OrderUpdate(**updated_order)

    @staticmethod
    async def delete_order(session: AsyncSession,
                           order_id: int,
                           user_current: dict) -> int:
        await order_service.check_existing_user_order(session=session, user_current=user_current, order_id=order_id)

        return await OrderRepository(session=session).delete_one(id_data=order_id)


class OrderItemService:

    @staticmethod
    async def add_order_item(order_item_data: OrderItemCreate,
                             session: AsyncSession,
                             redis_client: Redis,
                             user_current: dict) -> int:
        await order_service.check_existing_user_order(session=session,
                                                      user_current=user_current,
                                                      order_id=order_item_data.order_id)

        product: dict = await product_service.get_product(id_product=order_item_data.product_id, session=session)

        if order_item_data.quantity > product["quantity"]:
            raise HttpAPIException(exception="there is no such quantity of products available").http_error_400

        if not order_item_data.total_price:
            order_item_data.total_price = order_item_data.quantity * order_item_data.price

        order_item_dict: dict[str, Any] = order_item_data.model_dump()
        order_item_id: int = await OrderItemRepository(session=session).add_one(data=order_item_dict)
        await redis_client.set(name=f"modified_order_{order_item_data.order_id}", value="True")
        return order_item_id

    @staticmethod
    async def get_order_items(session: AsyncSession,
                              order_id: int) -> list[OrderItemShow]:
        all_order_item_list = await OrderItemRepository(session=session).find_all_by_param(param_column="order_id",
                                                                                           param_value=order_id)
        schemas_order_items: list[OrderItemShow] = [OrderItemShow(**data) for data in all_order_item_list]
        return schemas_order_items


order_service = OrderService()
order_item_service = OrderItemService()
