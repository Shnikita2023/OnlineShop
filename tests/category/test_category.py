import pytest
from httpx import AsyncClient, Response


class TestCategory:
    """Класс для тестирования категории"""

    @pytest.mark.parametrize(
        "name, description",
        [
            ("телефоны", "Телефоны нового поколение"),
            ("телевизоры", "Товар с Китая"),
            ("планшеты", "Ультратонкие")
        ]
    )
    async def test_create_category(self,
                                   async_client: AsyncClient,
                                   get_cookie_is_superuser: dict[str, str],
                                   name: str,
                                   description: str) -> None:
        response_category: Response = await async_client.post(url="/api/v1/categories/",
                                                              headers=get_cookie_is_superuser,
                                                              json={
                                                                  "name": name,
                                                                  "description": description,
                                                              })
        assert response_category.status_code == 201

    async def test_get_category(self, async_client: AsyncClient) -> None:
        response_category: Response = await async_client.get(url="/api/v1/categories/1")
        assert response_category.status_code == 200
        assert len(response_category.json()) == 3
        assert response_category.json()["name"] == "телефоны"
        assert response_category.json()["description"] == "Телефоны нового поколение"

    async def test_delete_category(self, async_client: AsyncClient, get_cookie_is_superuser: dict[str, str]) -> None:
        response: Response = await async_client.delete(url="/api/v1/categories/1",
                                                       headers=get_cookie_is_superuser)
        assert response.status_code == 204

    async def test_get_categories(self, async_client: AsyncClient) -> None:
        response_categories: Response = await async_client.get(url="/api/v1/categories/")
        assert response_categories.status_code == 200
        assert len(response_categories.json()) == 2
        assert response_categories.json()[0]["name"] == "телевизоры"
        assert response_categories.json()[1]["description"] == "Ультратонкие"

