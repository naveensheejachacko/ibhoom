from fastapi import APIRouter
from .products import router as products_router
from .profile import router as profile_router
from .orders import router as orders_router

router = APIRouter()

# Include all seller sub-routers
router.include_router(products_router, prefix="/products", tags=["Seller - Products"])
router.include_router(profile_router, prefix="/profile", tags=["Seller - Profile"])
router.include_router(orders_router, prefix="/orders", tags=["Seller - Orders"]) 