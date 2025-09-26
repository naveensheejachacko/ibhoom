from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....models.user import User
from ....models.order import OrderStatus, PaymentStatus
from ....schemas.order import OrderResponse, OrderListResponse, OrderStatusUpdate, PaymentStatusUpdate, OrderStats
from ....services import order_service

router = APIRouter()


@router.get("/stats", response_model=OrderStats)
async def get_order_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get order statistics (Admin only)"""
    stats = order_service.get_order_stats(db)
    return OrderStats(**stats)


@router.get("/", response_model=List[OrderListResponse])
async def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    customer_id: Optional[str] = Query(None),
    status: Optional[OrderStatus] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all orders with filtering (Admin only)"""
    orders = order_service.get_orders(
        db, skip=skip, limit=limit,
        customer_id=customer_id, status=status, payment_status=payment_status
    )
    return orders


@router.get("/pending", response_model=List[OrderListResponse])
async def get_pending_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get pending orders (Admin only)"""
    orders = order_service.get_pending_orders(db, skip=skip, limit=limit)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get order by ID (Admin only)"""
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update order status (Admin only)"""
    updated_order = order_service.update_order_status(db, order_id, status_update)
    if not updated_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return updated_order


@router.put("/{order_id}/payment", response_model=OrderResponse)
async def update_payment_status(
    order_id: str,
    payment_update: PaymentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update payment status (Admin only)"""
    updated_order = order_service.update_payment_status(db, order_id, payment_update)
    if not updated_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return updated_order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    admin_notes: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Cancel order and restore stock (Admin only)"""
    try:
        cancelled_order = order_service.cancel_order(db, order_id, admin_notes)
        if not cancelled_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return cancelled_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) 