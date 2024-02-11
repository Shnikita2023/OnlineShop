from datetime import datetime

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Order(Base):
    __tablename__ = "order"

    total_price: Mapped[float] = mapped_column(default=0.0)
    cost_delivery: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50))
    payment_method: Mapped[str] = mapped_column(String(50))

    user_id: Mapped[int] = mapped_column(ForeignKey(column="user.id", ondelete="CASCADE"), unique=True)
    user: Mapped["User"] = relationship(back_populates="orders")

    order_items: Mapped["OrderItem"] = relationship(back_populates="order")

    def __str__(self):
        return f"Заказ {self.user_id}"


class OrderItem(Base):
    __tablename__ = 'order_item'

    quantity: Mapped[int]
    order_date: Mapped[datetime] = mapped_column(server_default=func.now())
    address: Mapped[str] = mapped_column(String(100))
    price: Mapped[float]
    total_price: Mapped[float]

    order_id: Mapped[int] = mapped_column(ForeignKey(column='order.id', ondelete="CASCADE"))
    order: Mapped["Order"] = relationship(back_populates="order_items")

    product_id: Mapped[int] = mapped_column(ForeignKey(column='product.id', ondelete="CASCADE"))
    product: Mapped["Product"] = relationship(back_populates="order_item")

    def __str__(self):
        return f"Элемент заказа {self.order_id}"
