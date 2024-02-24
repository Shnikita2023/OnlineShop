from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    quantity: int
    name_image: str
    category_id: int
    discount: float = Field(default=0.0)


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
    discount: float | None = None
