from fastapi import APIRouter
from .orders import router as orders_router
from .products import router as products_router
from .reviews import router as reviews_router
from . import categories as categories_router

router = APIRouter()

# Include all customer sub-routers
router.include_router(orders_router, prefix="/orders", tags=["Customer - Orders"])
router.include_router(products_router, prefix="/products", tags=["Customer - Products"])
router.include_router(reviews_router, prefix="/reviews", tags=["Customer - Reviews"]) 
router.include_router(categories_router.router, prefix="/categories", tags=["Customer - Categories"])