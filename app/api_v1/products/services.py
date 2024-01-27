from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.exceptions import CustomException
from app.api_v1.products.repository import ProductRepository
from app.api_v1.products.schemas import ProductCreate, ProductUpdate


class ProductService:

    @staticmethod
    async def add_product(product_data: ProductCreate, session: AsyncSession) -> int:
        product_dict: dict[str, Any] = product_data.model_dump()
        return await ProductRepository(session=session).add_one(data=product_dict)

    @staticmethod
    async def get_products(session: AsyncSession) -> list[dict[str, Any]]:
        return await ProductRepository(session=session).find_all()

    @staticmethod
    async def get_product(id_product: int, session: AsyncSession) -> Optional[dict]:
        product = await ProductRepository(session=session).find_one(id_data=id_product)
        if product:
            return product
        raise CustomException(exception="product is not found").http_error_400

    @staticmethod
    async def get_product_by_param(param_colum_product: str,
                                   product_value: Any,
                                   session: AsyncSession) -> Optional[dict]:
        product = await ProductRepository(session=session).find_one_by_param(param_column=param_colum_product,
                                                                             param_value=product_value)
        if product:
            return product
        raise CustomException(exception="product is not found").http_error_400

    @staticmethod
    async def delete_product(id_product: int, session: AsyncSession) -> int:
        return await ProductRepository(session=session).delete_one(id_data=id_product)

    @staticmethod
    async def update_product(id_product: int,
                             session: AsyncSession,
                             new_product: ProductUpdate) -> dict[str, Any]:
        new_product: dict[str, Any] = new_product.model_dump()
        return await ProductRepository(session=session).update_one(id_data=id_product, new_data=new_product)


product_service = ProductService()
