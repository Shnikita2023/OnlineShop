from abc import abstractmethod, ABC

from app.api_v1.cart.repository import CartRepository, CartItemRepository
from app.api_v1.categories.repository import CategoryRepository
from app.api_v1.orders.repository import OrderRepository, OrderItemRepository
from app.api_v1.products.repository import ProductRepository
from app.api_v1.profiles.repository import ProfileRepository


class IUnitOfWork(ABC):
    category: CategoryRepository
    product: ProductRepository
    profile: ProfileRepository
    cart: CartRepository
    cart_item: CartItemRepository
    order: OrderRepository
    order_item: OrderItemRepository

    @abstractmethod
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(self, *args) -> None:
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    async def __aenter__(self) -> None:
        self.session = self.session_factory()

        self.category = CategoryRepository(self.session)
        self.product = ProductRepository(self.session)
        self.profile = ProfileRepository(self.session)
        self.cart = CartRepository(self.session)
        self.cart_item = CartItemRepository(self.session)
        self.order = OrderRepository(self.session)
        self.order_item = OrderItemRepository(self.session)

    async def __aexit__(self, *args) -> None:
        await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
