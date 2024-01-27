from pydantic import BaseModel, ConfigDict


class CartItemCreate(BaseModel):
    quantity: int
    price: float
    cart_id: int
    product_id: int


class CartItemUpdatePartial(BaseModel):
    quantity: int | None = None
    price: float | None = None
    cart_id: int | None = None
    product_id: int | None = None


class CartItemShow(CartItemCreate):
    model_config = ConfigDict(strict=True)
    id: int


class CartItemUpdate(CartItemCreate):
    pass


class CartCreate(BaseModel):
    user_id: int


class CartShow(CartCreate):
    model_config = ConfigDict(strict=True)
    id: int
