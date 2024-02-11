import pytest

from app.api_v1.categories import Category
from tests.conftest import async_session_maker_test


@pytest.fixture(scope="session")
async def get_category_id() -> int:
    """Фикстура для получения id категории"""
    new_category = {"name": "телефоны", "description": "Телефоны нового поколение"}
    async with async_session_maker_test() as session:
        category = Category(**new_category)
        session.add(category)
        await session.flush()
        await session.commit()
        return category.id
