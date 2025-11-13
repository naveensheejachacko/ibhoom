from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
from ....core.database import get_db
from ....core.dependencies import get_seller_user
from ....models.user import User
from ....models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ....models.product import Product, ProductVariant, ProductImage
from ....schemas.order import OrderResponse, OrderListResponse, OrderListItemResponse, OrderItemResponse, SellerOrderStatusUpdate
from ....schemas.pagination import PaginatedResponse
from ....services import order_service

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[OrderListResponse])
async def get_my_orders(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
    skip: Optional[int] = Query(None, ge=0, description="Skip items (alternative to page, deprecated)"),
    status: Optional[OrderStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Get seller's orders (orders containing seller's products) (Seller only)"""
    # Calculate skip from page if not provided
    if skip is None:
        skip = (page - 1) * limit
    
    seller_id = current_user.seller.id
    
    # Get all order items that belong to this seller's products
    order_items_query = db.query(OrderItem.order_id).join(Product).filter(
        Product.seller_id == seller_id
    ).distinct()
    
    # Get orders with eager loading of items and related data
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.seller),
        joinedload(Order.items).joinedload(OrderItem.variant)
    ).filter(Order.id.in_(order_items_query))
    
    if status:
        query = query.filter(Order.status == status)
    
    # Get total count before pagination
    total = query.count()
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    # Build response with product details
    order_responses = []
    for order in orders:
        # Build items with product details (only seller's items)
        items = []
        for item in order.items:
            # Only include items that belong to this seller
            if item.product.seller_id != seller_id:
                continue
                
            product = item.product
            variant = item.variant if item.product_variant_id else None
            
            # Get product image - try primary first, then any image
            primary_image = db.query(ProductImage).filter(
                ProductImage.product_id == product.id,
                ProductImage.is_primary == True
            ).first()
            
            if not primary_image:
                # Fallback to any image if no primary image
                any_image = db.query(ProductImage).filter(
                    ProductImage.product_id == product.id
                ).order_by(ProductImage.sort_order.asc()).first()
                product_image = any_image.image_url if any_image else None
            else:
                product_image = primary_image.image_url
            
            # Get seller name
            seller_name = product.seller.business_name if product.seller else None
            
            items.append(OrderListItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_variant_id=item.product_variant_id,
                product_name=item.product_name,
                variant_name=variant.variant_name if variant else None,
                product_image=product_image,
                seller_name=seller_name,
                quantity=item.quantity,
                customer_unit_price=float(item.customer_unit_price),
                total_customer_amount=float(item.total_customer_amount)
            ))
        
        order_responses.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            customer_id=order.customer_id,
            total_customer_amount=float(order.total_customer_amount),
            total_items=order.total_items,
            status=order.status,
            payment_status=order.payment_status,
            created_at=order.created_at,
            items=items
        ))
    
    # Calculate pagination metadata
    current_page = page  # Use the provided page parameter
    pages = (total + limit - 1) // limit if total > 0 else 1
    
    return PaginatedResponse(
        items=order_responses,
        total=total,
        page=current_page,
        size=limit,
        pages=pages
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_my_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Get seller's order by ID (Seller only)"""
    seller_id = current_user.seller.id
    
    # Get order with eager loading of items and related data
    order = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.seller),
        joinedload(Order.items).joinedload(OrderItem.variant)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Verify order contains seller's products
    seller_items = [item for item in order.items if item.product.seller_id == seller_id]
    if not seller_items:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="This order does not contain your products"
        )
    
    # Build items with product details (only seller's items)
    items_with_details = []
    for item in order.items:
        # Only include items that belong to this seller
        if item.product.seller_id != seller_id:
            continue
            
        product = item.product
        variant = item.variant if item.product_variant_id else None
        
        # Get product image - try primary first, then any image
        primary_image = db.query(ProductImage).filter(
            ProductImage.product_id == product.id,
            ProductImage.is_primary == True
        ).first()
        
        if not primary_image:
            # Fallback to any image if no primary image
            any_image = db.query(ProductImage).filter(
                ProductImage.product_id == product.id
            ).order_by(ProductImage.sort_order.asc()).first()
            product_image = any_image.image_url if any_image else None
        else:
            product_image = primary_image.image_url
        
        # Create item response with product details
        items_with_details.append(OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            product_variant_id=item.product_variant_id,
            quantity=item.quantity,
            seller_unit_price=float(item.seller_unit_price),
            customer_unit_price=float(item.customer_unit_price),
            commission_unit_rate=float(item.commission_unit_rate),
            commission_unit_amount=float(item.commission_unit_amount),
            total_seller_amount=float(item.total_seller_amount),
            total_customer_amount=float(item.total_customer_amount),
            total_commission_amount=float(item.total_commission_amount),
            product_name=item.product_name,
            variant_name=variant.variant_name if variant else None,
            product_image=product_image
        ))
    
    # Create order response with enhanced items
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        customer_id=order.customer_id,
        total_customer_amount=float(order.total_customer_amount),
        total_seller_amount=float(order.total_seller_amount),
        total_commission_amount=float(order.total_commission_amount),
        status=order.status,
        payment_status=order.payment_status,
        delivery_address=order.delivery_address,
        delivery_city=order.delivery_city,
        delivery_state=order.delivery_state,
        delivery_pincode=order.delivery_pincode,
        phone=order.phone,
        notes=order.notes,
        admin_notes=order.admin_notes,
        seller_notes=order.seller_notes,
        return_reason=order.return_reason,
        return_notes=order.return_notes,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=items_with_details
    )


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

