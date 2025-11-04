from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from ....core.database import get_db
from ....core.dependencies import get_seller_user
from ....models.user import User
from ....models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ....models.product import Product
from ....schemas.order import OrderResponse, OrderListResponse, SellerOrderStatusUpdate
from ....services import order_service

router = APIRouter()


@router.get("/", response_model=List[OrderListResponse])
async def get_my_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[OrderStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Get seller's orders (orders containing seller's products) (Seller only)"""
    seller_id = current_user.seller.id
    
    # Get all order items that belong to this seller's products
    order_items_query = db.query(OrderItem.order_id).join(Product).filter(
        Product.seller_id == seller_id
    ).distinct()
    
    # Get orders from those order items
    query = db.query(Order).filter(Order.id.in_(order_items_query))
    
    if status:
        query = query.filter(Order.status == status)
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_my_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Get seller's order by ID (Seller only)"""
    seller_id = current_user.seller.id
    
    # Check if order contains seller's products
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Verify order belongs to seller
    seller_items = [item for item in order.items if item.product.seller_id == seller_id]
    if not seller_items:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="This order does not contain your products"
        )
    
    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: SellerOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Update order status (Seller only - can reject, cancel, processing, ready_for_dispatch)"""
    seller_id = current_user.seller.id
    
    # Get order and verify it belongs to seller
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Verify order contains seller's products
    seller_items = [item for item in order.items if item.product.seller_id == seller_id]
    if not seller_items:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="This order does not contain your products"
        )
    
    # Validate status transition (Seller can only set specific statuses)
    allowed_statuses = [
        OrderStatus.REJECTED,
        OrderStatus.CANCELLED,
        OrderStatus.PROCESSING,
        OrderStatus.READY_FOR_DISPATCH
    ]
    
    if status_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Seller can only set status to: {[s.value for s in allowed_statuses]}"
        )
    
    # Validate status transitions
    current_status = order.status
    
    # Can reject/cancel from pending or processing
    if status_update.status in [OrderStatus.REJECTED, OrderStatus.CANCELLED]:
        if current_status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot {status_update.status.value} order from {current_status.value} status"
            )
        
        # If rejecting/cancelling, restore stock
        for item in seller_items:
            if item.product_variant_id:
                variant = db.query(ProductVariant).filter(ProductVariant.id == item.product_variant_id).first()
                if variant:
                    variant.stock_quantity += item.quantity
            else:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.stock_quantity += item.quantity
    
    # Can set to processing from pending
    elif status_update.status == OrderStatus.PROCESSING:
        if current_status != OrderStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Can only set to processing from pending status"
            )
    
    # Can set to ready_for_dispatch from processing
    elif status_update.status == OrderStatus.READY_FOR_DISPATCH:
        if current_status != OrderStatus.PROCESSING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Can only set to ready_for_dispatch from processing status"
            )
    
    # Update order status
    order.status = status_update.status
    if status_update.seller_notes:
        order.seller_notes = status_update.seller_notes
    order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order

