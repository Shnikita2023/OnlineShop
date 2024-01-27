from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.api_v1.cart.schemas import CartItemShow, CartShow
from app.db import Base


class Cart(Base):
    __tablename__ = "carts"

    user_id: Mapped[int] = mapped_column(ForeignKey(column="users.id", ondelete="CASCADE"), unique=True)
    user = relationship(argument="User", back_populates="cart")

    cart_items = relationship(argument="CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = 'cart_items'

    quantity: Mapped[int]
    price: Mapped[float]
    added_at: Mapped[datetime] = mapped_column(server_default=func.now())

    cart_id: Mapped[int] = mapped_column(ForeignKey(column='carts.id', ondelete="CASCADE"))
    cart = relationship(argument="Cart", back_populates="cart_items")

    product_id: Mapped[int] = mapped_column(ForeignKey(column='products.id', ondelete="CASCADE"), unique=True)
    products = relationship(argument="Product", back_populates="cart_items")
