from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    name_image: str
    category_id: int


class ProductShow(ProductCreate):
    model_config = ConfigDict(strict=True)
    id: int


class ProductUpdate(ProductCreate):
    pass


class ProductUpdatePartial(BaseModel):
    name: str | None = None
    description: str | None = None
    price: int | None = None
    quantity: int | None = None
    name_image: str | None = None
