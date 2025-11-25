from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from pathlib import Path
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....models.user import User
from ....models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ....models.product import Product, ProductVariant, ProductImage
from ....schemas.order import (
    OrderResponse, OrderListResponse, OrderListItemResponse, OrderItemResponse,
    OrderStatusUpdate, PaymentStatusUpdate, OrderStats, ReturnStatusUpdate
)
from ....schemas.pagination import PaginatedResponse
from ....services import order_service

router = APIRouter()


@router.get("/stats", response_model=OrderStats)
async def get_order_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get order statistics (Admin only)"""
    try:
        stats = order_service.get_order_stats(db)
        return OrderStats(**stats)
    except Exception as e:
        print(f"Error in admin orders stats endpoint: {e}")
        # Return default stats if there's an error
        return OrderStats(
            total_orders=0,
            pending_orders=0,
            processing_orders=0,
            shipped_orders=0,
            delivered_orders=0,
            cancelled_orders=0,
            total_revenue=0.0,
            total_commission=0.0
        )


@router.get("/", response_model=PaginatedResponse[OrderListResponse])
async def get_all_orders(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
    skip: Optional[int] = Query(None, ge=0, description="Skip items (alternative to page, deprecated)"),
    customer_id: Optional[str] = Query(None),
    status: Optional[OrderStatus] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    search: Optional[str] = Query(None, description="Search by order number"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all orders with filtering (Admin only)"""
    # Calculate skip from page if not provided
    if skip is None:
        skip = (page - 1) * limit
    
    # Build query with eager loading
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.seller),
        joinedload(Order.items).joinedload(OrderItem.variant)
    )
    
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    if status:
        query = query.filter(Order.status == status)
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    if search:
        query = query.filter(Order.order_number.ilike(f"%{search}%"))
    
    # Get total count before pagination
    total = query.count()
    
    orders = query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    # Build response with product details
    order_responses = []
    for order in orders:
        # Build items with product details
        items = []
        for item in order.items:
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
                total_customer_amount=float(item.total_customer_amount),
                tax_rate=float(item.tax_rate),
                tax_unit_amount=float(item.tax_unit_amount),
                total_tax_amount=float(item.total_tax_amount),
                final_unit_price=float(item.final_unit_price),
                total_final_amount=float(item.total_final_amount)
            ))
        
        order_responses.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            customer_id=order.customer_id,
            total_customer_amount=float(order.total_customer_amount),
            total_tax_amount=float(order.total_tax_amount),
            grand_total_amount=float(order.grand_total_amount),
            payable_amount=float(order.total_seller_amount),  # Amount payable to seller(s)
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


@router.get("/pending", response_model=PaginatedResponse[OrderListResponse])
async def get_pending_orders(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
    skip: Optional[int] = Query(None, ge=0, description="Skip items (alternative to page, deprecated)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get pending orders (Admin only)"""
    # Calculate skip from page if not provided
    if skip is None:
        skip = (page - 1) * limit
    
    # Build query with eager loading
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.seller),
        joinedload(Order.items).joinedload(OrderItem.variant)
    ).filter(Order.status == OrderStatus.PENDING)
    
    # Get total count before pagination
    total = query.count()
    
    orders = query.order_by(Order.created_at.asc()).offset(skip).limit(limit).all()
    
    # Build response with product details
    order_responses = []
    for order in orders:
        # Build items with product details
        items = []
        for item in order.items:
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
            total_customer_amount=float(item.total_customer_amount),
            tax_rate=float(item.tax_rate),
            tax_unit_amount=float(item.tax_unit_amount),
            total_tax_amount=float(item.total_tax_amount),
            final_unit_price=float(item.final_unit_price),
            total_final_amount=float(item.total_final_amount)
            ))
        
        order_responses.append(OrderListResponse(
            id=order.id,
            order_number=order.order_number,
            customer_id=order.customer_id,
            total_customer_amount=float(order.total_customer_amount),
            total_tax_amount=float(order.total_tax_amount),
            grand_total_amount=float(order.grand_total_amount),
            payable_amount=float(order.total_seller_amount),  # Amount payable to seller(s)
            total_items=order.total_items,
            status=order.status,
            payment_status=order.payment_status,
            created_at=order.created_at,
            items=items
        ))
    
    # Calculate pagination metadata
    current_page = page
    pages = (total + limit - 1) // limit if total > 0 else 1
    
    return PaginatedResponse(
        items=order_responses,
        total=total,
        page=current_page,
        size=limit,
        pages=pages
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get order by ID (Admin only)"""
    # Get order with eager loading of items and related data
    order = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.seller),
        joinedload(Order.items).joinedload(OrderItem.variant)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Build items with product details
    items_with_details = []
    for item in order.items:
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
            tax_rate=float(item.tax_rate),
            tax_unit_amount=float(item.tax_unit_amount),
            total_tax_amount=float(item.total_tax_amount),
            final_unit_price=float(item.final_unit_price),
            total_final_amount=float(item.total_final_amount),
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
        total_tax_amount=float(order.total_tax_amount),
        grand_total_amount=float(order.grand_total_amount),
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
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update order status (Admin only - can set dispatched, delivered, cancelled)"""
    try:
        updated_order = order_service.update_order_status_admin(db, order_id, status_update)
        if not updated_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


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


@router.put("/{order_id}/return", response_model=OrderResponse)
async def handle_return(
    order_id: str,
    return_update: ReturnStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Handle return request (Admin only - approve, reject, or accept return completion)"""
    try:
        updated_order = order_service.handle_return(db, order_id, return_update)
        if not updated_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        return updated_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{order_id}/invoice")
async def download_invoice(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Download invoice PDF for a delivered order (Admin only)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check if order is delivered
    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice can only be generated for delivered orders"
        )
    
    # Generate invoice on the fly (don't save to disk to save space)
    try:
        from ....utils.invoice import generate_invoice_pdf
        import os
        
        # Generate invoice without saving
        invoice_buffer = generate_invoice_pdf(order, output_path=None)
        
        # Delete any existing invoice file if it exists (cleanup)
        backend_dir = Path(__file__).parent.parent.parent.parent.parent
        invoice_dir = backend_dir / "static" / "invoices"
        invoice_file = invoice_dir / f"invoice_{order.order_number}.pdf"
        if invoice_file.exists():
            try:
                os.remove(invoice_file)
            except Exception:
                pass  # Ignore deletion errors
        
        return Response(
            content=invoice_buffer.getvalue(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="invoice_{order.order_number}.pdf"'
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate invoice: {str(e)}"
        ) 