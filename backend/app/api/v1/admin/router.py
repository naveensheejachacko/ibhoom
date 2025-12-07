from fastapi import APIRouter
from .categories import router as categories_router
from .commissions import router as commissions_router
from .products import router as products_router
from .users import router as users_router
from .orders import router as orders_router
from .attributes import router as attributes_router
from .notifications import router as notifications_router
from .banners import router as banners_router
from .fcm_token import router as fcm_token_router
from .profile import router as profile_router

router = APIRouter()

# Include all admin sub-routers
router.include_router(categories_router, prefix="/categories", tags=["Admin - Categories"])
router.include_router(commissions_router, prefix="/commissions", tags=["Admin - Commissions"])
router.include_router(products_router, prefix="/products", tags=["Admin - Products"])
router.include_router(users_router, prefix="/users", tags=["Admin - Users"])
router.include_router(orders_router, prefix="/orders", tags=["Admin - Orders"])
router.include_router(attributes_router, prefix="/attributes", tags=["Admin - Attributes"])
router.include_router(notifications_router, prefix="/notifications", tags=["Admin - Notifications"])
router.include_router(banners_router, prefix="/banners", tags=["Admin - Banners"])
router.include_router(fcm_token_router, prefix="/fcm-token", tags=["Admin - FCM Token"])
router.include_router(profile_router, prefix="/profile", tags=["Admin - Profile"]) 