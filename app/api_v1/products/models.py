from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.api_v1.categories import Category
# from app.api_v1.cart import CartItem
from app.api_v1.products.schemas import ProductShow
from app.db import Base


class Product(Base):
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[float] = mapped_column(default=0.0)
    description: Mapped[str | None]
    quantity: Mapped[int] = mapped_column(default=0)
    name_image: Mapped[str] = mapped_column(unique=True)

    category_id: Mapped[int] = mapped_column(ForeignKey(column="categories.id", ondelete="CASCADE"))
    categories = relationship(argument="Category", back_populates="products")

    cart_items = relationship(argument="CartItem", back_populates="products")
    order_items = relationship(argument="OrderItem", back_populates="products")

