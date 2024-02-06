from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.categories import CategoryCreate, CategoryUpdate, CategoryShow
from app.api_v1.categories.repository import CategoryRepository
from app.api_v1.exceptions import HttpAPIException


class CategoryService:

    @staticmethod
    async def add_category(category_data: CategoryCreate, session: AsyncSession) -> int:
        category_dict: dict[str, Any] = category_data.model_dump()
        return await CategoryRepository(session=session).add_one(data=category_dict)

    @staticmethod
    async def get_categories(session: AsyncSession) -> Optional[list[CategoryShow]]:
        all_category_list: list[dict] = await CategoryRepository(session=session).find_all()
        schemas_category: list[CategoryShow] = [CategoryShow(**data) for data in all_category_list]
        return schemas_category

    @staticmethod
    async def get_category(id_category: int, session: AsyncSession) -> CategoryShow:
        category: dict = await CategoryRepository(session=session).find_one(id_data=id_category)

        if category:
            return CategoryShow(**category)

        raise HttpAPIException(exception="id categories is not found").http_error_400

    @staticmethod
    async def delete_category(id_category: int, session: AsyncSession) -> int:
        return await CategoryRepository(session=session).delete_one(id_data=id_category)

    @staticmethod
    async def update_category(id_category: int,
                              session: AsyncSession,
                              new_category: CategoryUpdate) -> dict[str, Any]:
        new_category: dict[str, Any] = new_category.model_dump()
        return await CategoryRepository(session=session).update_one(id_data=id_category,
                                                                    new_data=new_category)


category_service = CategoryService()
