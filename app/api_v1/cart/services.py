from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.cart.repository import CartItemRepository, CartRepository
from app.api_v1.cart.schemas import (CartItemCreate, CartCreate, CartItemShow,
                                     CartItemUpdatePartial, CartItemUpdate, CartShow)

from app.api_v1.exceptions import HttpAPIException
from app.api_v1.products.schemas import ProductUpdatePartial
from app.api_v1.products.services import product_service


class CartItemService:
    """
    Сервис элементов корзины
    """

    @staticmethod
    async def _check_existing_user_cart(session: AsyncSession,
                                        user_current: dict,
                                        cart_id: int) -> None:
        """Проверка существование корзины пользователя и его прав доступа"""
        cart_user: CartShow = await CartService.get_cart(session=session, cart_id=cart_id)

        if cart_user.user_id != user_current["sub"]:
            raise HttpAPIException(exception="access denied.").http_error_403

    @staticmethod
    async def add_cart_item(cart_item_data: CartItemCreate,
                            session: AsyncSession,
                            user_current: dict) -> int:
        """Добавление элемента в корзину пользователя"""
        await cart_item_service._check_existing_user_cart(session=session,
                                                          user_current=user_current,
                                                          cart_id=cart_item_data.cart_id)

        cart_items: list[dict[str, Any]] = await CartItemRepository(session=session).find_all()
        for item in cart_items:
            if item["product_id"] == cart_item_data.product_id:
                raise HttpAPIException(exception="this product already exists in cart_items").http_error_400

        await product_service.reserve_product_quantity(product_id=cart_item_data.product_id,
                                                       quantity_products=cart_item_data.quantity,
                                                       session=session)

        cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
        return await CartItemRepository(session=session).add_one(data=cart_item_dict)

    @staticmethod
    async def get_cart_items(session: AsyncSession, user_current: dict) -> list[CartItemShow]:
        """Получение всех элементов корзины"""
        await cart_service.get_cart_by_param(session=session,
                                             value_cart=user_current["sub"],
                                             name_column="user_id")

        cart_items: list[dict[str, Any]] = await CartItemRepository(session=session).find_all()

        return [CartItemShow(**data) for data in cart_items]

    @staticmethod
    async def get_cart_item(session: AsyncSession, user_current: dict, cart_item_id: int) -> CartItemShow:
        """Получение элемента корзины"""
        cart_item: Optional[dict] = await CartItemRepository(session=session).find_one(id_data=cart_item_id)

        if not cart_item:
            raise HttpAPIException(exception="element cart not found").http_error_400

        await cart_item_service._check_existing_user_cart(session=session,
                                                          user_current=user_current,
                                                          cart_id=cart_item["cart_id"])
        return CartItemShow(**cart_item)

    @staticmethod
    async def delete_cart_item(session: AsyncSession, cart_item_id: int, user_current: dict) -> int:
        """Удаление элемента корзины"""
        cart_item: CartItemShow = await cart_item_service.get_cart_item(session=session,
                                                                        user_current=user_current,
                                                                        cart_item_id=cart_item_id)
        product_by_cart: dict = await product_service.get_product(id_product=cart_item.product_id, session=session)
        new_reserved_quantity: int = product_by_cart["reserved_quantity"] - cart_item.quantity
        updated_product: ProductUpdatePartial = ProductUpdatePartial(reserved_quantity=new_reserved_quantity)
        await product_service.update_product_partial(id_product=cart_item.product_id,
                                                     new_product=updated_product,
                                                     session=session)

        return await CartItemRepository(session=session).delete_one(id_data=cart_item_id)

    @staticmethod
    async def update_partial_cart_item(session: AsyncSession,
                                       cart_item_id: int,
                                       cart_item_data: CartItemUpdatePartial,
                                       user_current: dict) -> CartItemUpdatePartial:
        """Частичное обновление элемента корзины"""
        await cart_item_service._check_existing_user_cart(session=session,
                                                          user_current=user_current,
                                                          cart_id=cart_item_data.cart_id)

        await product_service.get_product(id_product=cart_item_data.product_id, session=session)

        cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
        new_cart_item_partial = await CartItemRepository(session=session).update_one(id_data=cart_item_id,
                                                                                     new_data=cart_item_dict)
        return CartItemUpdatePartial(**new_cart_item_partial)

    @staticmethod
    async def update_cart_item(session: AsyncSession,
                               cart_item_id: int,
                               cart_item_data: CartItemUpdate,
                               user_current: dict) -> CartItemUpdate:
        """Обновление элемента корзины"""
        await cart_item_service._check_existing_user_cart(session=session,
                                                          user_current=user_current,
                                                          cart_id=cart_item_data.cart_id)

        await product_service.get_product(id_product=cart_item_data.product_id, session=session)
        cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
        new_cart_item = await CartItemRepository(session=session).update_one(id_data=cart_item_id,
                                                                             new_data=cart_item_dict)
        return CartItemUpdate(**new_cart_item)


class CartService:
    """
    Сервис корзины
    """

    @staticmethod
    async def add_cart(cart_data: CartCreate, session: AsyncSession) -> int:
        """Добавление корзины пользователя"""
        cart: dict = await CartRepository(session=session).find_one_by_param(param_column="user_id",
                                                                             param_value=cart_data.user_id)
        if not cart:
            cart_dict: dict[str, Any] = cart_data.model_dump()
            return await CartRepository(session=session).add_one(data=cart_dict)

        raise HttpAPIException(exception="cart already exist").http_error_400

    @staticmethod
    async def delete_cart(session: AsyncSession, user_id: int) -> int:
        """Удаление корзины пользователя"""
        cart: CartShow = await cart_service.get_cart_by_param(session=session, value_cart=user_id,
                                                              name_column="user_id")
        return await CartRepository(session=session).delete_one(id_data=cart.id)

    @staticmethod
    async def get_cart(session: AsyncSession, cart_id: int) -> CartShow:
        """Получение корзины пользователя"""
        cart: Optional[dict] = await CartRepository(session=session).find_one(id_data=cart_id)

        if cart:
            return CartShow(**cart)

        raise HttpAPIException(exception="cart is not found").http_error_400

    @staticmethod
    async def get_cart_by_param(session: AsyncSession, value_cart: Any, name_column: str) -> CartShow:
        """Получение корзины пользователя по фильтрам"""
        cart: Optional[dict] = await CartRepository(session=session).find_one_by_param(param_column=name_column,
                                                                                       param_value=value_cart)
        if cart:
            return CartShow(**cart)

        raise HttpAPIException(exception="cart is not found").http_error_400


cart_item_service = CartItemService()
cart_service = CartService()
