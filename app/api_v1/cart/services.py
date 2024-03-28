from typing import Any, Optional

from app.api_v1.cart.schemas import (CartItemCreate, CartCreate, CartItemShow,
                                     CartItemUpdatePartial, CartItemUpdate, CartShow)

from app.api_v1.exceptions import HttpAPIException
from app.api_v1.products.schemas import ProductUpdatePartial
from app.api_v1.products.services import product_service
from app.api_v1.utils.unitofwork import IUnitOfWork


class CartItemService:
    """
    Сервис элементов корзины
    """

    @staticmethod
    async def _check_existing_user_cart(uow: IUnitOfWork,
                                        user_current: dict,
                                        cart_id: int) -> None:
        """Проверка существование корзины пользователя и его прав доступа"""
        cart_user: CartShow = await CartService.get_cart(uow=uow, cart_id=cart_id)

        if cart_user.user_id != user_current["sub"]:
            raise HttpAPIException(exception="access denied.").http_error_403

    @staticmethod
    async def add_cart_item(cart_item_data: CartItemCreate,
                            uow: IUnitOfWork,
                            user_current: dict) -> int:
        """Добавление элемента в корзину пользователя"""
        await cart_item_service._check_existing_user_cart(uow=uow,
                                                          user_current=user_current,
                                                          cart_id=cart_item_data.cart_id)
        async with uow:
            cart_items: list[dict[str, Any]] = await uow.cart_item.find_all()
            for item in cart_items:
                if item["product_id"] == cart_item_data.product_id:
                    raise HttpAPIException(exception="this product already exists in cart_items").http_error_400

            await product_service.reserve_product_quantity(product_id=cart_item_data.product_id,
                                                           quantity_products=cart_item_data.quantity,
                                                           uow=uow)

            cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
            cart_item_id: int = await uow.cart_item.add_one(data=cart_item_dict)
            await uow.commit()
            return cart_item_id

    @staticmethod
    async def get_cart_items(uow: IUnitOfWork, user_current: dict) -> list[CartItemShow]:
        """Получение всех элементов корзины"""
        await cart_service.get_cart_by_param(uow=uow,
                                             value_cart=user_current["sub"],
                                             name_column="user_id")
        async with uow:
            cart_items: list[dict[str, Any]] = await uow.cart_item.find_all()

            return [CartItemShow(**data) for data in cart_items]

    @staticmethod
    async def get_cart_item(uow: IUnitOfWork, user_current: dict, cart_item_id: int) -> CartItemShow:
        """Получение элемента корзины"""
        async with uow:
            cart_item: Optional[dict] = await uow.cart_item.find_one(id_data=cart_item_id)

            if not cart_item:
                raise HttpAPIException(exception="element cart not found").http_error_400

            await cart_item_service._check_existing_user_cart(uow=uow,
                                                              user_current=user_current,
                                                              cart_id=cart_item["cart_id"])
            return CartItemShow(**cart_item)

    @staticmethod
    async def delete_cart_item(uow: IUnitOfWork, cart_item_id: int, user_current: dict) -> int:
        """Удаление элемента корзины"""
        cart_item: CartItemShow = await cart_item_service.get_cart_item(uow=uow,
                                                                        user_current=user_current,
                                                                        cart_item_id=cart_item_id)
        product_by_cart: dict = await product_service.get_product(id_product=cart_item.product_id, uow=uow)
        new_reserved_quantity: int = product_by_cart["reserved_quantity"] - cart_item.quantity
        updated_product: ProductUpdatePartial = ProductUpdatePartial(reserved_quantity=new_reserved_quantity)
        await product_service.update_product_partial(id_product=cart_item.product_id,
                                                     new_product=updated_product,
                                                     uow=uow)
        async with uow:
            deleted_cart_item: int = await uow.cart_item.delete_one(id_data=cart_item_id)
            await uow.commit()
            return deleted_cart_item

    @staticmethod
    async def update_partial_cart_item(uow: IUnitOfWork,
                                       cart_item_id: int,
                                       cart_item_data: CartItemUpdatePartial,
                                       user_current: dict) -> CartItemUpdatePartial:
        """Частичное обновление элемента корзины"""
        await cart_item_service._check_existing_user_cart(uow=uow,
                                                          user_current=user_current,
                                                          cart_id=cart_item_data.cart_id)

        await product_service.get_product(id_product=cart_item_data.product_id, uow=uow)

        cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
        async with uow:
            new_cart_item_partial = await uow.cart_item.update_one(id_data=cart_item_id,
                                                                   new_data=cart_item_dict)
            await uow.commit()
            return CartItemUpdatePartial(**new_cart_item_partial)

    @staticmethod
    async def update_cart_item(uow: IUnitOfWork,
                               cart_item_id: int,
                               cart_item_data: CartItemUpdate,
                               user_current: dict) -> CartItemUpdate:
        """Обновление элемента корзины"""
        await cart_item_service._check_existing_user_cart(uow=uow,
                                                          user_current=user_current,
                                                          cart_id=cart_item_data.cart_id)

        await product_service.get_product(id_product=cart_item_data.product_id, uow=uow)
        cart_item_dict: dict[str, Any] = cart_item_data.model_dump()
        async with uow:
            new_cart_item = await uow.cart_item.update_one(id_data=cart_item_id,
                                                           new_data=cart_item_dict)
            await uow.commit()
            return CartItemUpdate(**new_cart_item)


class CartService:
    """
    Сервис корзины
    """

    @staticmethod
    async def add_cart(cart_data: CartCreate, uow: IUnitOfWork) -> int:
        """Добавление корзины пользователя"""
        async with uow:
            cart: dict = await uow.cart.find_one_by_param(param_column="user_id",
                                                          param_value=cart_data.user_id)

            if not cart:
                cart_dict: dict[str, Any] = cart_data.model_dump()
                cart_id: int = await uow.cart.add_one(data=cart_dict)
                await uow.commit()
                return cart_id

            raise HttpAPIException(exception="cart already exists").http_error_400

    @staticmethod
    async def delete_cart(uow: IUnitOfWork, user_id: int) -> int:
        """Удаление корзины пользователя"""

        cart: CartShow = await cart_service.get_cart_by_param(uow=uow, value_cart=user_id,
                                                              name_column="user_id")
        async with uow:
            deleted_cart = await uow.cart.delete_one(id_data=cart.id)
            await uow.commit()
            return deleted_cart

    @staticmethod
    async def get_cart(uow: IUnitOfWork, cart_id: int) -> CartShow:
        """Получение корзины пользователя"""
        async with uow:
            cart: Optional[dict] = await uow.cart.find_one(id_data=cart_id)

            if cart:
                return CartShow(**cart)

            raise HttpAPIException(exception="cart is not found").http_error_400

    @staticmethod
    async def get_cart_by_param(uow: IUnitOfWork, value_cart: Any, name_column: str) -> CartShow:
        """Получение корзины пользователя по фильтрам"""
        async with uow:
            cart: Optional[dict] = await uow.cart.find_one_by_param(param_column=name_column,
                                                                    param_value=value_cart)
            if cart:
                return CartShow(**cart)

            raise HttpAPIException(exception="cart is not found").http_error_400


cart_item_service = CartItemService()
cart_service = CartService()
