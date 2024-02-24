from fastapi import APIRouter

from .products.routers import router as products_router
from .users.routers import router as users_router
from .profiles.routers import router as profiles_router
from .categories.routers import router as categories_router
from .cart.routers import router_cart, router_cart_item
from .orders.routers import router_order, router_order_item
from .tasks.routers import router as notifications_router

router = APIRouter()
router.include_router(router=users_router)
router.include_router(router=profiles_router)
router.include_router(router=categories_router)
router.include_router(router=products_router)
router.include_router(router=router_cart)
router.include_router(router=router_cart_item)
router.include_router(router=router_order)
router.include_router(router=router_order_item)
router.include_router(router=notifications_router)
