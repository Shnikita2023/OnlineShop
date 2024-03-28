from typing import Any, Optional

from redis.asyncio.client import Redis

from app.api_v1.exceptions import HttpAPIException
from app.api_v1.orders import OrderCreate, OrderItemCreate, OrderItemShow, OrderUpdate, OrderShow
from app.api_v1.products.services import product_service
from app.api_v1.utils.unitofwork import IUnitOfWork


class OrderService:
    """
    Сервис заказов
    """

    @staticmethod
    async def check_existing_user_order(uow: IUnitOfWork, user_current: dict, order_id: int) -> None:
        """Проверка существующего заказа и доступа пользователя"""
        async with uow:
            order: Optional[dict] = await uow.order.find_one(id_data=order_id)

            if not order:
                raise HttpAPIException(exception="order not found").http_error_400

            if user_current["sub"] != order["user_id"]:
                raise HttpAPIException(exception="access denied").http_error_403

            return None

    @staticmethod
    async def create_order(order_data: OrderCreate, uow: IUnitOfWork, redis_client: Redis) -> int:
        """Создание заказа"""
        order_dict: dict[str, Any] = order_data.model_dump()
        async with uow:
            order_id: int = await uow.order.add_one(data=order_dict)
            await uow.commit()
            await redis_client.set(name=f"modified_order_{order_id}", value="False")

            return order_id

    @staticmethod
    async def get_order(uow: IUnitOfWork,
                        redis_client: Redis,
                        user_current: dict,
                        order_id: int) -> OrderShow:
        """Получение заказа"""
        await order_service.check_existing_user_order(uow=uow, user_current=user_current, order_id=order_id)

        is_modified_order_id: bool = await redis_client.get(f"modified_order_{order_id}")
        all_items_order: list[OrderItemShow] = await OrderItemService.get_order_items(uow=uow,
                                                                                      order_id=order_id)
        async with uow:
            if is_modified_order_id:
                summa_total_price: float = sum(data.total_price for data in all_items_order)
                new_order = {"total_price": summa_total_price, "status": "Ready"}
                await uow.order.update_one(id_data=order_id, new_data=new_order)
                await uow.commit()
                await redis_client.set(name=f"modified_order_{order_id}", value="False")

            order_user: Optional[dict] = await uow.order.find_one(id_data=order_id)
            return OrderShow(**order_user)

    @staticmethod
    async def update_order(uow: IUnitOfWork,
                           order_id: int,
                           new_order: OrderUpdate,
                           user_current: dict) -> OrderUpdate:
        """Обновление заказа"""
        if user_current["sub"] != new_order.user_id:
            raise HttpAPIException(exception="access denied.").http_error_403

        order_dict: dict[str, Any] = new_order.model_dump()
        async with uow:
            updated_order = await uow.order.update_one(id_data=order_id, new_data=order_dict)
            await uow.commit()
            return OrderUpdate(**updated_order)

    @staticmethod
    async def delete_order(uow: IUnitOfWork,
                           order_id: int,
                           user_current: dict) -> int:
        """Удаление заказа"""
        await order_service.check_existing_user_order(uow=uow, user_current=user_current, order_id=order_id)
        async with uow:
            deleted_order_id: int = await uow.order.delete_one(id_data=order_id)
            await uow.commit()
            return deleted_order_id


class OrderItemService:
    """
    Сервис элементов заказа
    """

    @staticmethod
    async def add_order_item(order_item_data: OrderItemCreate,
                             uow: IUnitOfWork,
                             redis_client: Redis,
                             user_current: dict) -> int:
        """Добавление элемента заказа"""
        await order_service.check_existing_user_order(uow=uow,
                                                      user_current=user_current,
                                                      order_id=order_item_data.order_id)
        product: dict = await product_service.get_product(id_product=order_item_data.product_id, uow=uow)

        if order_item_data.quantity > product["quantity"]:
            raise HttpAPIException(exception="there is no such quantity of products available").http_error_400

        if not order_item_data.total_price:
            order_item_data.total_price = order_item_data.quantity * order_item_data.price

        order_item_dict: dict[str, Any] = order_item_data.model_dump()
        async with uow:
            order_item_id: int = await uow.order_item.add_one(data=order_item_dict)
            await uow.commit()
            await redis_client.set(name=f"modified_order_{order_item_data.order_id}", value="True")
            return order_item_id

    @staticmethod
    async def get_order_items(uow: IUnitOfWork,
                              order_id: int) -> list[OrderItemShow]:
        """Получение элемента заказа"""
        async with uow:
            all_order_item_list = await uow.order_item.find_all_by_param(param_column="order_id",
                                                                         param_value=order_id)
            schemas_order_items: list[OrderItemShow] = [OrderItemShow(**data) for data in all_order_item_list]
            return schemas_order_items


order_service = OrderService()
order_item_service = OrderItemService()
