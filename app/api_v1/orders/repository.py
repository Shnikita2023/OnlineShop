from app.api_v1.orders import Order, OrderItem
from app.api_v1.repositories.base_repository import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository):
    model = Order


class OrderItemRepository(SQLAlchemyRepository):
    model = OrderItem
