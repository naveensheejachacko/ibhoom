from fastapi import APIRouter
from .orders import router as orders_router
from .products import router as products_router
from .reviews import router as reviews_router
from .cart import router as cart_router
from .wishlist import router as wishlist_router
from .banners import router as banners_router
from . import categories as categories_router

router = APIRouter()

# Include all customer sub-routers
router.include_router(orders_router, prefix="/orders", tags=["Customer - Orders"])
router.include_router(products_router, prefix="/products", tags=["Customer - Products"])
router.include_router(reviews_router, prefix="/reviews", tags=["Customer - Reviews"])
router.include_router(cart_router, prefix="/cart", tags=["Customer - Cart"])
router.include_router(wishlist_router, prefix="/wishlist", tags=["Customer - Wishlist"])
router.include_router(banners_router, prefix="/banners", tags=["Customer - Banners"])
router.include_router(categories_router.router, prefix="/categories", tags=["Customer - Categories"])