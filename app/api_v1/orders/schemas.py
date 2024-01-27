from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    total_price: float = 0.0
    cost_delivery: str = "Free"
    status: str = "Not Ready"
    payment_method: str = "Sberbank"
    user_id: int


class OrderShow(OrderCreate):
    model_config = ConfigDict(strict=True)
    id: int


class OrderUpdate(OrderCreate):
    pass


class OrderItemCreate(BaseModel):
    quantity: int
    address: str
    price: float
    total_price: float | None = None
    order_id: int
    product_id: int


class OrderItemShow(OrderItemCreate):
    model_config = ConfigDict(strict=True)
    id: int
