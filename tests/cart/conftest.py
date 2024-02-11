import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.cart import Cart
from app.api_v1.categories import Category
from app.api_v1.products import Product
from tests.conftest import async_session_maker_test


async def get_category(session: AsyncSession) -> int:
    """Фикстура для получения id категории"""
    new_category: dict[str, str] = {"name": "телефоны", "description": "Телефоны нового поколение"}
    category: Category = Category(**new_category)
    session.add(category)
    await session.flush()
    await session.commit()
    return category.id


@pytest.fixture(scope="session")
async def get_product_id() -> int:
    """Фикстура для получения id продукта"""
    async with async_session_maker_test() as session:
        category_id: int = await get_category(session=session)
        product: Product = Product(name="Samsung A5",
                                   description="Диагональ 6.5",
                                   price=55000.0,
                                   quantity=100,
                                   name_image="samsung_a5",
                                   category_id=category_id)
        session.add(product)
        await session.flush()
        await session.commit()
        return product.id


@pytest.fixture(scope="session")
async def get_cart_id() -> int:
    """Фикстура для получения id корзины"""
    async with async_session_maker_test() as session:
        cart: Cart = Cart(user_id=1)
        session.add(cart)
        await session.flush()
        await session.commit()
        return cart.id
