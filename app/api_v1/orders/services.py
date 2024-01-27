from typing import Any

from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.exceptions import CustomException
from app.api_v1.orders import OrderCreate, OrderItemCreate, OrderItemShow, OrderUpdate
from app.api_v1.orders.repository import OrderRepository, OrderItemRepository


class OrderItemService:

    @staticmethod
    async def add_order_item(order_item_data: OrderItemCreate,
                             session: AsyncSession,
                             redis_client: Redis,
                             user_current: dict) -> int:
        if not order_item_data.total_price:
            order_item_data.total_price = order_item_data.quantity * order_item_data.price
        order_item_dict: dict[str, Any] = order_item_data.model_dump()
        order_item_id: int = await OrderItemRepository(session=session).add_one(data=order_item_dict)
        await redis_client.set(name=f"modified_order_{order_item_data.order_id}", value="True")
        return order_item_id

    @staticmethod
    async def get_order_items(session: AsyncSession,
                              user_current: dict,
                              order_id: int) -> list[OrderItemShow]:
        all_order_item_list = await OrderItemRepository(session=session).find_by_param(param_column="order_id",
                                                                                       value=order_id)
        schemas_order_items: list[OrderItemShow] = [OrderItemShow(**data) for data in all_order_item_list]
        return schemas_order_items

    #
    # @staticmethod
    # async def get_cart_item(session: AsyncSession, user_current: dict, cart_item_id: int) -> CartItemShow:
    #     cart_item: CartItemShow = await CartItemRepository(session=session).find_one(id_data=cart_item_id)
    #     if not cart_item:
    #         raise CustomException(exception="element cart not found").http_error_400
    #     cart_user: CartShow = await CartService.get_cart(session=session, cart_id=cart_item.cart_id)
    #     if cart_user.user_id != user_current["sub"]:
    #         raise CustomException(exception="access denied.").http_error_403
    #     return cart_item
    #
    # @staticmethod
    # async def delete_cart_item(session: AsyncSession, cart_item_id: int, user_current: dict) -> int:
    #     await CartItemService.get_cart_item(session=session, user_current=user_current, cart_item_id=cart_item_id)
    #     return await CartItemRepository(session=session).delete_one(id_data=cart_item_id)
    #
    # @staticmethod
    # async def update_partial_cart_item(session: AsyncSession,
    #                                    cart_item_id: int,
    #                                    cart_item_data: CartItemUpdatePartial) -> dict[str, Any]:
    #     cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
    #     return await CartItemRepository(session=session).update_one(id_data=cart_item_id,
    #                                                                 new_data=cart_item_dict)
    #
    # @staticmethod
    # async def update_cart_item(session: AsyncSession,
    #                            cart_item_id: int,
    #                            cart_item_data: CartItemUpdate) -> dict[str, Any]:
    #     cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
    #     return await CartItemRepository(session=session).update_one(id_data=cart_item_id,
    #                                                                 new_data=cart_item_dict)


class OrderService:

    @staticmethod
    async def add_order(order_data: OrderCreate, session: AsyncSession, redis_client: Redis) -> int:
        order_dict: dict[str, Any] = order_data.model_dump()
        order_id: int = await OrderRepository(session=session).add_one(data=order_dict)
        await redis_client.set(name=f"modified_order_{order_id}", value="False")
        return order_id

    @staticmethod
    async def get_order(session: AsyncSession,
                        redis_client: Redis,
                        user_current: dict,
                        order_id: int) -> dict:
        order = await OrderRepository(session=session).find_one(id_data=order_id)
        if not order:
            raise CustomException(exception="order not found").http_error_400
        is_modified_order_id: bool = await redis_client.get(f"modified_order_{order_id}")
        if is_modified_order_id == "True":
            all_items_order: list[OrderItemShow] = await OrderItemService.get_order_items(session=session,
                                                                                          user_current=user_current,
                                                                                          order_id=order_id)

            summa_total_price: float = sum(data.total_price for data in all_items_order)
            new_order = {"total_price": summa_total_price, "status": "Ready"}
            await OrderRepository(session=session).update_one(id_data=order_id, new_data=new_order)
            await redis_client.set(name=f"modified_order_{order_id}", value="False")
            return await OrderRepository(session=session).find_one(id_data=order_id)
        return order

    @staticmethod
    async def update_order(session: AsyncSession, order_id: int, new_order: OrderUpdate) -> dict:
        order_dict: dict[str, Any] = new_order.model_dump()
        return await OrderRepository(session=session).update_one(id_data=order_id, new_data=order_dict)
    #
    # @staticmethod
    # async def get_cart(session: AsyncSession, cart_id: int) -> CartShow:
    #     cart = await CartRepository(session=session).find_one(id_data=cart_id)
    #     if cart:
    #         return cart
    #     raise CustomException(exception="cart is not found").http_error_400


order_item_service = OrderItemService()
order_service = OrderService()
