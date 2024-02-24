from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.categories.services import category_service
from app.api_v1.exceptions import HttpAPIException
from app.api_v1.products import Product
from app.api_v1.products.repository import ProductRepository
from app.api_v1.products.schemas import ProductCreate, ProductUpdate, ProductUpdatePartial


class ProductService:
    """
    Сервис продуктов
    """

    @staticmethod
    async def add_product(product_data: ProductCreate, session: AsyncSession) -> int:
        """Добавление продукта"""
        await category_service.get_category(id_category=product_data.category_id,
                                            session=session)
        product_dict: dict[str, Any] = product_data.model_dump()
        new_price_by_discount: float = product_dict["price"] * (1 - product_dict["discount"])
        product_dict["price"] = new_price_by_discount
        return await ProductRepository(session=session).add_one(data=product_dict)

    @staticmethod
    async def get_products(session: AsyncSession) -> list[dict[str, Any]]:
        """Получение продуктов"""
        return await ProductRepository(session=session).find_all()

    @staticmethod
    async def get_products_only_discount(session: AsyncSession) -> Optional[list[Product]]:
        """Получение продуктов со скидкой"""
        return await ProductRepository(session=session).find_all_greater_than(param_column="discount",
                                                                              param_value=0)

    @staticmethod
    async def get_product(id_product: int, session: AsyncSession) -> dict:
        """Получение продукта"""
        product = await ProductRepository(session=session).find_one(id_data=id_product)

        if product:
            return product

        raise HttpAPIException(exception="product is not found").http_error_400

    @staticmethod
    async def get_product_by_param(param_colum_product: str,
                                   product_value: Any,
                                   session: AsyncSession) -> Optional[dict]:
        """Получение продукта по параметрам"""
        product = await ProductRepository(session=session).find_one_by_param(param_column=param_colum_product,
                                                                             param_value=product_value)
        if product:
            return product

        raise HttpAPIException(exception="product is not found").http_error_400

    @staticmethod
    async def delete_product(id_product: int, session: AsyncSession) -> int:
        """Удаление продукта"""
        return await ProductRepository(session=session).delete_one(id_data=id_product)

    @staticmethod
    async def update_product(id_product: int,
                             session: AsyncSession,
                             new_product: ProductUpdate) -> dict[str, Any]:
        """Обновление продукта"""
        new_product: dict[str, Any] = new_product.model_dump()
        return await ProductRepository(session=session).update_one(id_data=id_product, new_data=new_product)

    @staticmethod
    async def update_product_partial(id_product: int,
                                     session: AsyncSession,
                                     new_product: ProductUpdatePartial) -> dict[str, Any]:
        """Частичное обновление продукта"""
        new_product: dict[str, Any] = new_product.dict(exclude_none=True)
        return await ProductRepository(session=session).update_one(id_data=id_product, new_data=new_product)

    @staticmethod
    async def reserve_product_quantity(product_id: int, quantity_products: int, session: AsyncSession):
        """Резервирование количество продуктов"""
        product: dict = await product_service.get_product(id_product=product_id, session=session)

        if quantity_products <= product["quantity"] - product["reserved_quantity"]:
            product["reserved_quantity"] += quantity_products
            await ProductRepository(session=session).update_one(id_data=product_id, new_data=product)

        else:
            raise HttpAPIException(exception="not enough available quantity for reservation").http_error_400


product_service = ProductService()
