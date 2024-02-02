from typing import Any, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.cart.repository import CartItemRepository, CartRepository
from app.api_v1.cart.schemas import (CartItemCreate, CartCreate, CartItemShow,
                                     CartItemUpdatePartial, CartItemUpdate, CartShow)

from app.api_v1.exceptions import HttpAPIException


class CartItemService:

    @staticmethod
    async def add_cart_item(cart_item_data: CartItemCreate,
                            session: AsyncSession,
                            user_current: dict) -> int:
        try:
            cart_user: CartShow = await CartService.get_cart(session=session, cart_id=cart_item_data.cart_id)

            if cart_user.user_id == user_current["sub"]:
                cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
                return await CartItemRepository(session=session).add_one(data=cart_item_dict)

            raise HttpAPIException(exception="access denied.").http_error_403

        except IntegrityError:
            raise HttpAPIException(exception="the product in cart already exists").http_error_400

    @staticmethod
    async def get_cart_items(session: AsyncSession, user_current: dict, cart_id: int) -> list[CartItemShow]:
        cart_user: CartShow = await CartService.get_cart(session=session, cart_id=cart_id)

        if cart_user.user_id == user_current["sub"]:
            return await CartItemRepository(session=session).find_by_param(param_column="cart_id", value=cart_id)

        raise HttpAPIException(exception="access denied.").http_error_403

    @staticmethod
    async def get_cart_item(session: AsyncSession, user_current: dict, cart_item_id: int) -> CartItemShow:
        cart_item: CartItemShow = await CartItemRepository(session=session).find_one(id_data=cart_item_id)

        if not cart_item:
            raise HttpAPIException(exception="element cart not found").http_error_400

        cart_user: CartShow = await CartService.get_cart(session=session, cart_id=cart_item.cart_id)

        if cart_user.user_id != user_current["sub"]:
            raise HttpAPIException(exception="access denied.").http_error_403

        return cart_item

    @staticmethod
    async def delete_cart_item(session: AsyncSession, cart_item_id: int, user_current: dict) -> int:
        await CartItemService.get_cart_item(session=session, user_current=user_current, cart_item_id=cart_item_id)
        return await CartItemRepository(session=session).delete_one(id_data=cart_item_id)

    @staticmethod
    async def update_partial_cart_item(session: AsyncSession,
                                       cart_item_id: int,
                                       cart_item_data: CartItemUpdatePartial) -> dict[str, Any]:
        cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
        return await CartItemRepository(session=session).update_one(id_data=cart_item_id,
                                                                    new_data=cart_item_dict)

    @staticmethod
    async def update_cart_item(session: AsyncSession,
                               cart_item_id: int,
                               cart_item_data: CartItemUpdate) -> dict[str, Any]:
        cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
        return await CartItemRepository(session=session).update_one(id_data=cart_item_id,
                                                                    new_data=cart_item_dict)


class CartService:

    @staticmethod
    async def add_cart(cart_data: CartCreate, session: AsyncSession) -> int:
        cart: dict = await CartRepository(session=session).find_one_by_param(param_column="user_id",
                                                                             param_value=cart_data.user_id)
        if not cart:
            cart_dict: dict[str, Any] = cart_data.model_dump()
            return await CartRepository(session=session).add_one(data=cart_dict)

        raise HttpAPIException(exception="cart already exist").http_error_400

    @staticmethod
    async def delete_cart(session: AsyncSession, user_id: int) -> int:
        return await CartRepository(session=session).delete_one(id_data=user_id)

    @staticmethod
    async def get_cart(session: AsyncSession, cart_id: int) -> CartShow:
        cart: dict = await CartRepository(session=session).find_one(id_data=cart_id)

        if cart:
            return CartShow(**cart)

        raise HttpAPIException(exception="cart is not found").http_error_400

    @staticmethod
    async def get_cart_by_param(session: AsyncSession, value_cart: Any, name_column: str) -> CartShow:
        cart: Optional[dict] = await CartRepository(session=session).find_one_by_param(param_column=name_column,
                                                                                       param_value=value_cart)
        if cart:
            return CartShow(**cart)

        raise HttpAPIException(exception="cart is not found").http_error_400


cart_item_service = CartItemService()
cart_service = CartService()
