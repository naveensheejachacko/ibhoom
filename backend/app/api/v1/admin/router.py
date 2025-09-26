from fastapi import APIRouter
from .categories import router as categories_router
from .commissions import router as commissions_router
from .products import router as products_router
from .users import router as users_router
from .orders import router as orders_router

router = APIRouter()

# Include all admin sub-routers
router.include_router(categories_router, prefix="/categories", tags=["Admin - Categories"])
router.include_router(commissions_router, prefix="/commissions", tags=["Admin - Commissions"])
router.include_router(products_router, prefix="/products", tags=["Admin - Products"])
router.include_router(users_router, prefix="/users", tags=["Admin - Users"])
router.include_router(orders_router, prefix="/orders", tags=["Admin - Orders"]) 