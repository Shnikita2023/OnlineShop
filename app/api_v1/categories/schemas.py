from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    description: str


class CategoryShow(CategoryCreate):
    model_config = ConfigDict(strict=True)
    id: int


class CategoryUpdate(CategoryCreate):
    pass
