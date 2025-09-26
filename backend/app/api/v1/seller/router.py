from fastapi import APIRouter
from .products import router as products_router

router = APIRouter()

# Include all seller sub-routers
router.include_router(products_router, prefix="/products", tags=["Seller - Products"]) 