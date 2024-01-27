from app.api_v1.categories import Category
from app.api_v1.repositories.base_repository import SQLAlchemyRepository


class CategoryRepository(SQLAlchemyRepository):
    model = Category



