from app.api_v1.cart import Cart, CartItem
from app.api_v1.repositories.base_repository import SQLAlchemyRepository


class CartRepository(SQLAlchemyRepository):
    model = Cart


class CartItemRepository(SQLAlchemyRepository):
    model = CartItem
