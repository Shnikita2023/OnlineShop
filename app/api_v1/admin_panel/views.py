from sqladmin import ModelView

from app.api_v1.cart import Cart, CartItem
from app.api_v1.categories import Category
from app.api_v1.orders import Order, OrderItem
from app.api_v1.products import Product
from app.api_v1.profiles import Profile
from app.api_v1.users.models import User


class UserAdmin(ModelView, model=User):
    column_list = ("id", "username", "email", "is_active", "is_superuser",
                   "is_verified", "profile", "orders", "cart")
    form_columns = ("username", "email", "is_active", "is_superuser", "is_verified")
    column_details_exclude_list = [User.password]
    can_delete = False
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"


class ProfileAdmin(ModelView, model=Profile):
    column_list = "__all__"
    name = "Профиль"
    name_plural = "Профили"


class CategoryAdmin(ModelView, model=Category):
    column_list = "__all__"
    form_columns = ("name", "description")
    name = "Категория"
    name_plural = "Категории"


class ProductAdmin(ModelView, model=Product):
    column_list = "__all__"
    form_columns = ("name", "description", "price", "quantity",
                    "reserved_quantity", "discount", "name_image", "category")
    name = "Продукт"
    name_plural = "Продукты"


class CartAdmin(ModelView, model=Cart):
    column_list = "__all__"
    name = "Корзина"
    name_plural = "Корзины"


class CartItemAdmin(ModelView, model=CartItem):
    column_list = "__all__"
    form_excluded_columns = ("added_at",)
    name = "Элемент корзины"
    name_plural = "Элементы корзины"


class OrderAdmin(ModelView, model=Order):
    column_list = "__all__"
    form_excluded_columns = ("order_items",)
    name = "Заказ"
    name_plural = "Заказы"


class OrderItemAdmin(ModelView, model=OrderItem):
    column_list = "__all__"
    form_excluded_columns = ("order_date",)
    name = "Элементы заказа"
    name_plural = "Элементы заказов"


admin_classes = [
    UserAdmin,
    ProfileAdmin,
    CategoryAdmin,
    ProductAdmin,
    CartAdmin,
    CartItemAdmin,
    OrderAdmin,
    OrderItemAdmin
]
