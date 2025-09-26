from fastapi import APIRouter
from .orders import router as orders_router

router = APIRouter()

# Include all customer sub-routers
router.include_router(orders_router, prefix="/orders", tags=["Customer - Orders"]) 