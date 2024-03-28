from typing import Any, Optional

from app.api_v1.categories import CategoryCreate, CategoryUpdate, CategoryShow
from app.api_v1.exceptions import HttpAPIException
from app.api_v1.utils.unitofwork import IUnitOfWork


class CategoryService:
    """
    Cервис категорий
    """

    @staticmethod
    async def add_category(category_data: CategoryCreate, uow: IUnitOfWork) -> int:
        """Добавление категории"""
        category_dict: dict[str, Any] = category_data.model_dump()
        async with uow:
            category_id: int = await uow.category.add_one(data=category_dict)
            await uow.commit()
            return category_id

    @staticmethod
    async def get_categories(uow: IUnitOfWork) -> Optional[list[CategoryShow]]:
        """Получение категорий"""
        async with uow:
            all_category_list: list[dict] = await uow.category.find_all()
            schemas_category: list[CategoryShow] = [CategoryShow(**data) for data in all_category_list]
            return schemas_category

    @staticmethod
    async def get_category(id_category: int, uow: IUnitOfWork) -> CategoryShow:
        """Получение категории"""
        async with uow:
            category: dict = await uow.category.find_one(id_data=id_category)

            if category:
                return CategoryShow(**category)

            raise HttpAPIException(exception="id categories is not found").http_error_400

    @staticmethod
    async def delete_category(id_category: int, uow: IUnitOfWork) -> int:
        """Удаление категории"""
        async with uow:
            deleted_category_id: int = await uow.category.delete_one(id_data=id_category)
            await uow.commit()
            return deleted_category_id

    @staticmethod
    async def update_category(id_category: int,
                              uow: IUnitOfWork,
                              new_category: CategoryUpdate) -> dict[str, Any]:
        """Обновление категории"""
        new_category: dict[str, Any] = new_category.model_dump()
        async with uow:
            updated_category = await uow.category.update_one(id_data=id_category,
                                                             new_data=new_category)
            await uow.commit()
            return updated_category


category_service = CategoryService()
