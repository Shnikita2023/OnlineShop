from httpx import Response, AsyncClient


class TestUserProfile:
    """
    Класс для работы c профилем пользователя
    """

    user_profile = {"user_id": 1, "first_name": "Ivan", "last_name": "Ivanov", "bio": "Занимается спортом"}
    update_user_profile = {"first_name": "Ivan", "last_name": "Ivanov", "bio": "Читает книги"}

    async def test_create_profile_user(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Cоздание профиля клиента"""
        response_profile: Response = await async_client.post(url="/api/v1/profiles/",
                                                             headers=get_cookie_user,
                                                             json=self.user_profile)
        assert response_profile.status_code == 201
        assert response_profile.json() == {"message": "the profile has been created successfully with number 1"}

    async def test_get_profile_user(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Получение профиля клиента"""
        response_profile: Response = await async_client.get(url="/api/v1/profiles/1",
                                                            headers=get_cookie_user)

        self.user_profile.update(id=1)
        assert response_profile.status_code == 200
        assert len(response_profile.json()) == 5
        assert response_profile.json() == self.user_profile

    async def test_update_profile_user(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Обновление профиля клиента"""
        response_update_profile: Response = await async_client.put(url="/api/v1/profiles/1",
                                                                   headers=get_cookie_user,
                                                                   json=self.update_user_profile)

        assert response_update_profile.status_code == 200
        assert response_update_profile.json() == self.update_user_profile

    async def test_delete_profile_user(self, async_client: AsyncClient, get_cookie_user: dict[str, str]) -> None:
        """Удаление профиля клиента"""
        response_delete_profile: Response = await async_client.delete(url="/api/v1/profiles/1",
                                                                      headers=get_cookie_user)

        assert response_delete_profile.status_code == 204

    async def test_get_profiles_users(self, async_client: AsyncClient, get_cookie_is_superuser: dict[str, str]) -> None:
        """Получение всех профилей клиентов"""
        response_profiles: Response = await async_client.get(url="/api/v1/profiles/",
                                                             headers=get_cookie_is_superuser)

        assert response_profiles.status_code == 200
        assert len(response_profiles.json()) == 0
        assert type(response_profiles.json()) == list
