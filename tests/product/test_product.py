import pytest
from httpx import Response, AsyncClient


class TestProduct:
    """Класс для тестирования продукта"""

    @pytest.mark.parametrize("name, description, price, quantity, name_image",
                             [
                                 ("Iphone 9", "Диагональ 6.0", 50000.0, 30, "iphone_9"),
                                 ("Samsung A5", "Диагональ 6.0", 20000.0, 100, "samsung_a5"),
                                 ("Xiaomi 7a", "Диагональ 7.0", 30000.0, 40, "xiaomi_7a")
                             ])
    async def test_create_product(self,
                                  name: str,
                                  description: str,
                                  price: float,
                                  quantity: int,
                                  name_image: str,
                                  get_category_id: int,
                                  async_client: AsyncClient,
                                  get_cookie_is_superuser: dict[str, str]) -> None:
        new_product = {
            "name": name,
            "description": description,
            "price": price,
            "quantity": quantity,
            "name_image": name_image,
            "category_id": get_category_id
        }

        response_product: Response = await async_client.post(url="/api/v1/products/",
                                                             headers=get_cookie_is_superuser,
                                                             json=new_product)
        assert response_product.status_code == 201
        assert response_product.json()["data"] == new_product

    async def test_get_product(self, async_client: AsyncClient) -> None:
        response_product: Response = await async_client.get(url="/api/v1/products/1")
        product = response_product.json()

        assert response_product.status_code == 200
        assert len(response_product.json()) == 7
        assert product["name"] == "Iphone 9"
        assert product["price"] == 50000.0

    async def test_delete_product(self, async_client: AsyncClient, get_cookie_is_superuser: dict[str, str]) -> None:
        response: Response = await async_client.delete(url="/api/v1/products/1",
                                                       headers=get_cookie_is_superuser)
        assert response.status_code == 204

    async def test_get_products(self, async_client: AsyncClient) -> None:
        response_products: Response = await async_client.get(url="/api/v1/products/all/")
        assert response_products.status_code == 200
        assert len(response_products.json()) == 2
