from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.api_v1.orders import OrderShow
from app.db import Base


class Order(Base):
    __tablename__ = "orders"

    total_price: Mapped[float]
    cost_delivery: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50))
    payment_method: Mapped[str] = mapped_column(String(50))

    user_id: Mapped[int] = mapped_column(ForeignKey(column="users.id", ondelete="CASCADE"), unique=True)
    user = relationship(argument="User", back_populates="orders")

    order_items = relationship(argument="OrderItem", back_populates="orders")


class OrderItem(Base):
    __tablename__ = 'order_items'

    quantity: Mapped[int]
    order_date: Mapped[datetime] = mapped_column(server_default=func.now())
    address: Mapped[str] = mapped_column(String(100))
    price: Mapped[float]
    total_price: Mapped[float]

    order_id: Mapped[int] = mapped_column(ForeignKey(column='orders.id', ondelete="CASCADE"))
    orders = relationship(argument="Order", back_populates="order_items")

    product_id: Mapped[int] = mapped_column(ForeignKey(column='products.id', ondelete="CASCADE"))
    products = relationship(argument="Product", back_populates="order_items")
