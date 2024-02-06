from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Product(Base):
    __tablename__ = "product"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[float] = mapped_column(default=0.0)
    description: Mapped[str | None]
    quantity: Mapped[int] = mapped_column(default=0)
    name_image: Mapped[str] = mapped_column(unique=True)

    category_id: Mapped[int] = mapped_column(ForeignKey(column="category.id", ondelete="CASCADE"))
    category = relationship(argument="Category", back_populates="products")

    cart_items = relationship(argument="CartItem", back_populates="products")
    order_items = relationship(argument="OrderItem", back_populates="products")

