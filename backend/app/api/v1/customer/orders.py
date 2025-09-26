from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_customer_user
from ....models.user import User
from ....models.order import OrderStatus, PaymentStatus
from ....schemas.order import OrderCreate, OrderResponse, OrderListResponse
from ....services import order_service

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Create a new order (Customer only)"""
    try:
        db_order = order_service.create_order(db, order, current_user.id)
        return db_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[OrderListResponse])
async def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[OrderStatus] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get customer's own orders (Customer only)"""
    orders = order_service.get_orders(
        db, skip=skip, limit=limit,
        customer_id=current_user.id, status=status, payment_status=payment_status
    )
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_my_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get customer's own order by ID (Customer only)"""
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check if customer owns the order
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this order")
    
    return order 