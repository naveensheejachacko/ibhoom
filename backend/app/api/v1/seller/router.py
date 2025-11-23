from fastapi import APIRouter
from .products import router as products_router
from .profile import router as profile_router
from .orders import router as orders_router
from .notifications import router as notifications_router
from .fcm_token import router as fcm_token_router
from .stock import router as stock_router

router = APIRouter()

# Include all seller sub-routers
router.include_router(products_router, prefix="/products", tags=["Seller - Products"])
router.include_router(profile_router, prefix="/profile", tags=["Seller - Profile"])
router.include_router(orders_router, prefix="/orders", tags=["Seller - Orders"]) 
router.include_router(notifications_router, prefix="/notifications", tags=["Seller - Notifications"])
router.include_router(fcm_token_router, prefix="/fcm-token", tags=["Seller - FCM Token"])
router.include_router(stock_router, prefix="/stock", tags=["Seller - Stock Management"]) 