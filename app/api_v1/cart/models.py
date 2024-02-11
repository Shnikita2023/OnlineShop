from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Cart(Base):
    __tablename__ = "cart"

    user_id: Mapped[int] = mapped_column(ForeignKey(column="user.id", ondelete="CASCADE"), unique=True)
    user: Mapped["User"] = relationship(back_populates="cart")

    cart_items: Mapped["CartItem"] = relationship(back_populates="cart")

    def __str__(self):
        return f"Корзина {self.user_id}"


class CartItem(Base):
    __tablename__ = 'cart_item'

    quantity: Mapped[int]
    price: Mapped[float]
    added_at: Mapped[datetime] = mapped_column(server_default=func.now())

    cart_id: Mapped[int] = mapped_column(ForeignKey(column='cart.id', ondelete="CASCADE"))
    cart: Mapped["Cart"] = relationship(back_populates="cart_items")

    product_id: Mapped[int] = mapped_column(ForeignKey(column='product.id', ondelete="CASCADE"), unique=True)
    product = relationship(argument="Product", back_populates="cart_item")

    def __str__(self):
        return f"Элемент корзины {self.cart_id}"
