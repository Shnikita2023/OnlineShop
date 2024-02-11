from httpx import AsyncClient, Response
from redis.asyncio.client import Redis


class TestUserOrder:
    """
    Класс для тестирования заказа пользователя
    """
    order_user = {
        "total_price": 0.0,
        "cost_delivery": "Free",
        "status": "Not Ready",
        "payment_method": "Sberbank",
        "user_id": 1
    }

    update_order_user = {
        "total_price": 0.0,
        "cost_delivery": "Not Free",
        "status": "Ready",
        "payment_method": "VTB",
        "user_id": 1
    }

    ready_order_user = {
        'total_price': 10000.0,
        'cost_delivery': 'Free',
        'status': 'Ready',
        'payment_method': 'Sberbank',
        'user_id': 1,
        'id': 1

    }

    async def test_create_order_user(self,
                                     async_client: AsyncClient,
                                     get_cookie_user: dict[str, str],
                                     async_redis_client: Redis) -> None:
        """Создание заказа пользователя"""
        response_order: Response = await async_client.post(url="/api/v1/orders/",
                                                           headers=get_cookie_user,
                                                           json=self.order_user)

        assert response_order.status_code == 201
        assert response_order.json() == {"message": "order created with 1 number successfully"}

    async def test_add_order_item(self,
                                  async_client: AsyncClient,
                                  get_cookie_user: dict[str, str],
                                  async_redis_client: Redis,
                                  get_product_id: int) -> None:
        """Добавление элемента к заказу пользователя"""
        order_item_user = {
            "quantity": 2,
            "address": "г.Москва, ул. Лермонтова",
            "price": 5000.0,
            "total_price": 0,
            "order_id": 1,
            "product_id": get_product_id
        }
        response_order_item: Response = await async_client.post(url="/api/v1/order_items/",
                                                                headers=get_cookie_user,
                                                                json=order_item_user)

        assert response_order_item.status_code == 201

    async def test_get_order_user(self,
                                  async_client: AsyncClient,
                                  get_cookie_user: dict[str, str],
                                  async_redis_client: Redis) -> None:
        """Получение заказа пользователя"""
        response_order_user: Response = await async_client.get(url="/api/v1/orders/1",
                                                               headers=get_cookie_user)

        assert response_order_user.status_code == 200
        assert response_order_user.json() == self.ready_order_user

    async def test_update_order_user(self,
                                     async_client: AsyncClient,
                                     get_cookie_user: dict[str, str],
                                     async_redis_client: Redis) -> None:
        """Обновление заказа пользователя"""
        response_update_order_user: Response = await async_client.put(url="/api/v1/orders/1",
                                                                      headers=get_cookie_user,
                                                                      json=self.update_order_user)
        assert response_update_order_user.status_code == 200
        assert response_update_order_user.json() == self.update_order_user

    async def test_delete_order_user(self,
                                     async_client: AsyncClient,
                                     get_cookie_user: dict[str, str],
                                     async_redis_client: Redis) -> None:
        """Удаление заказа пользователя"""
        response_order_user: Response = await async_client.delete(url="/api/v1/orders/1",
                                                                  headers=get_cookie_user)
        assert response_order_user.status_code == 204
