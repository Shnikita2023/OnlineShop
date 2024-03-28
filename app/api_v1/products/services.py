from typing import Any, Optional

from app.api_v1.categories.services import category_service
from app.api_v1.exceptions import HttpAPIException
from app.api_v1.products import Product

from app.api_v1.products.schemas import ProductCreate, ProductUpdate, ProductUpdatePartial
from app.api_v1.utils.unitofwork import IUnitOfWork


class ProductService:
    """
    Сервис продуктов
    """

    @staticmethod
    async def add_product(product_data: ProductCreate, uow: IUnitOfWork) -> int:
        """Добавление продукта"""
        await category_service.get_category(id_category=product_data.category_id,
                                            uow=uow)
        product_dict: dict[str, Any] = product_data.model_dump()
        new_price_by_discount: float = product_dict["price"] * (1 - product_dict["discount"])
        product_dict["price"] = new_price_by_discount
        async with uow:
            product_id: int = await uow.product.add_one(data=product_dict)
            await uow.commit()
            return product_id

    @staticmethod
    async def get_products(uow: IUnitOfWork) -> list[dict[str, Any]]:
        """Получение продуктов"""
        async with uow:
            return await uow.product.find_all()

    @staticmethod
    async def get_products_only_discount(uow: IUnitOfWork) -> Optional[list[Product]]:
        """Получение продуктов со скидкой"""
        async with uow:
            return await uow.product.find_all_greater_than(param_column="discount",
                                                           param_value=0)

    @staticmethod
    async def get_product(id_product: int, uow: IUnitOfWork) -> dict:
        """Получение продукта"""
        async with uow:
            product = await uow.product.find_one(id_data=id_product)

            if product:
                return product

            raise HttpAPIException(exception="product is not found").http_error_400

    @staticmethod
    async def get_product_by_param(param_colum_product: str,
                                   product_value: Any,
                                   uow: IUnitOfWork) -> Optional[dict]:
        """Получение продукта по параметрам"""
        async with uow:
            product = await uow.product.find_one_by_param(param_column=param_colum_product,
                                                          param_value=product_value)
            if product:
                return product

            raise HttpAPIException(exception="product is not found").http_error_400

    @staticmethod
    async def delete_product(id_product: int, uow: IUnitOfWork) -> int:
        """Удаление продукта"""
        async with uow:
            deleted_product_id: int = await uow.product.delete_one(id_data=id_product)
            await uow.commit()
            return deleted_product_id

    @staticmethod
    async def update_product(id_product: int,
                             uow: IUnitOfWork,
                             new_product: ProductUpdate) -> dict[str, Any]:
        """Обновление продукта"""
        new_product: dict[str, Any] = new_product.model_dump()
        async with uow:
            updated_product: dict[str, Any] = await uow.product.update_one(id_data=id_product, new_data=new_product)
            await uow.commit()
            return updated_product

    @staticmethod
    async def update_product_partial(id_product: int,
                                     uow: IUnitOfWork,
                                     new_product: ProductUpdatePartial) -> dict[str, Any]:
        """Частичное обновление продукта"""
        new_product: dict[str, Any] = new_product.dict(exclude_none=True)
        async with uow:
            updated_product: dict[str, Any] = await uow.product.update_one(id_data=id_product, new_data=new_product)
            await uow.commit()
            return updated_product

    @staticmethod
    async def reserve_product_quantity(product_id: int, quantity_products: int, uow: IUnitOfWork) -> None:
        """Резервирование количество продуктов"""
        product: dict = await product_service.get_product(id_product=product_id, uow=uow)

        async with uow:
            if quantity_products <= product["quantity"] - product["reserved_quantity"]:
                product["reserved_quantity"] += quantity_products
                await uow.product.update_one(id_data=product_id, new_data=product)
                await uow.commit()

            else:
                raise HttpAPIException(exception="not enough available quantity for reservation").http_error_400


product_service = ProductService()
