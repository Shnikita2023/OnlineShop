from httpx import AsyncClient, Response


class TestUserCart:
    """
    Класс для тестирования корзины
    """

    async def test_create_cart_user(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Создание корзины пользователя"""
        response_cart: Response = await async_client.post(url="/api/v1/cart/",
                                                          headers=get_cookie_user,
                                                          json={"user_id": 1})

        assert response_cart.status_code == 201

    async def test_get_cart_user(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Получение корзины пользователя"""
        response_cart: Response = await async_client.get(url="/api/v1/cart/1")
        assert response_cart.status_code == 200
        assert response_cart.json() == {'user_id': 1, 'id': 1}

    async def test_get_cart_user_by_id(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Получение корзины по id пользователя"""
        response_cart: Response = await async_client.get(url="/api/v1/cart/?user_id=1")
        assert response_cart.status_code == 200
        assert response_cart.json() == {'user_id': 1, 'id': 1}

    async def test_delete_cart_user(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Удаление корзины пользователя"""
        response_cart: Response = await async_client.delete(url="/api/v1/cart/1")
        assert response_cart.status_code == 204


class TestUserCartItems:
    """
    Класс для тестирования элементов корзины
    """

    async def test_create_cart_item(self,
                                    async_client: AsyncClient,
                                    get_cookie_user: dict[str, str],
                                    get_product_id: int,
                                    get_cart_id: int) -> None:
        """Создание элемента корзины"""
        cart_item = {"quantity": 1, "price": 15000, "cart_id": get_cart_id, "product_id": get_product_id}
        response_cart_item: Response = await async_client.post(url="/api/v1/cart_items/",
                                                               headers=get_cookie_user,
                                                               json=cart_item)

        assert response_cart_item.status_code == 201
        assert response_cart_item.json() == {"message": "element cart create with 1 number successfully"}

    async def test_get_cart_item(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Получение элемента корзины пользователя"""
        response_cart_item: Response = await async_client.get(url="/api/v1/cart_items/1")
        assert len(response_cart_item.json()) == 5
        assert response_cart_item.status_code == 200

    async def test_update_cart_item(self,
                                    async_client: AsyncClient,
                                    get_cookie_user: dict[str, str],
                                    get_product_id: int,
                                    get_cart_id: int) -> None:
        """Обновление элемента корзины пользователя"""
        new_cart_item = {"quantity": 12, "price": 20000, "cart_id": get_cart_id, "product_id": get_product_id}
        response_cart_item: Response = await async_client.put(url="/api/v1/cart_items/1",
                                                              headers=get_cookie_user,
                                                              json=new_cart_item)
        assert len(response_cart_item.json()) == 4
        assert response_cart_item.status_code == 200

    async def test_delete_cart_item(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Удаление элемента корзины пользователя"""
        response_cart_item: Response = await async_client.delete(url="/api/v1/cart_items/1")
        assert response_cart_item.status_code == 204
