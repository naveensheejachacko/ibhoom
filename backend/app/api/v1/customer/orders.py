from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import logging
from ....core.database import get_db
from ....core.dependencies import get_customer_user
from ....models.user import User
from ....models.order import Order, OrderStatus, PaymentStatus, OrderItem
from ....models.product import Product, ProductVariant, ProductImage
from ....schemas.order import OrderCreate, OrderResponse, OrderListResponse, OrderListItemResponse, OrderItemResponse, ReturnRequest
from ....schemas.pagination import PaginatedResponse
from ....services import order_service

logger = logging.getLogger(__name__)
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
        
        # Reload order with all relationships for response serialization
        # Use a fresh query to ensure clean transaction state
        # If previous query failed due to transaction issues, this will work
        try:
            db_order = db.query(Order).options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.items).joinedload(OrderItem.variant)
            ).filter(Order.id == db_order.id).first()
        except Exception as reload_error:
            # If reload fails due to transaction issues, rollback and try again
            logger.warning(f"First reload attempt failed: {reload_error}, retrying...")
            db.rollback()
            db_order = db.query(Order).options(
                joinedload(Order.items).joinedload(OrderItem.product),
                joinedload(Order.items).joinedload(OrderItem.variant)
            ).filter(Order.id == db_order.id).first()
        
        if not db_order:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Order created but could not be retrieved"
            )
        
        # Build response with product details
        items_with_details = []
        for item in db_order.items:
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
        
        # Return properly constructed response
        return OrderResponse(
            id=db_order.id,
            order_number=db_order.order_number,
            customer_id=db_order.customer_id,
            total_customer_amount=float(db_order.total_customer_amount),
            total_seller_amount=float(db_order.total_seller_amount),
            total_commission_amount=float(db_order.total_commission_amount),
            status=db_order.status,
            payment_status=db_order.payment_status,
            delivery_address=db_order.delivery_address,
            delivery_city=db_order.delivery_city,
            delivery_state=db_order.delivery_state,
            delivery_pincode=db_order.delivery_pincode,
            phone=db_order.phone,
            notes=db_order.notes,
            admin_notes=db_order.admin_notes,
            seller_notes=db_order.seller_notes,
            return_reason=db_order.return_reason,
            return_notes=db_order.return_notes,
            created_at=db_order.created_at,
            updated_at=db_order.updated_at,
            items=items_with_details
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        # Rollback transaction on any error
        db.rollback()
        logger.error(f"Error creating order: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@router.get("/", response_model=PaginatedResponse[OrderListResponse])
async def get_my_orders(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
    skip: Optional[int] = Query(None, ge=0, description="Skip items (alternative to page, deprecated)"),
    status: Optional[OrderStatus] = Query(None),
    payment_status: Optional[PaymentStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Get customer's own orders (Customer only)"""
    # Calculate skip from page if not provided
    if skip is None:
        skip = (page - 1) * limit
    
    # Get orders with eager loading of items and related data
    query = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.seller),
        joinedload(Order.items).joinedload(OrderItem.variant)
    ).filter(Order.customer_id == current_user.id)
    
    if status:
        query = query.filter(Order.status == status)
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    
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
    current_user: User = Depends(get_customer_user)
):
    """Get customer's own order by ID (Customer only)"""
    # Get order with eager loading of items and related data
    order = db.query(Order).options(
        joinedload(Order.items).joinedload(OrderItem.product).joinedload(Product.seller),
        joinedload(Order.items).joinedload(OrderItem.variant)
    ).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check if customer owns the order
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this order")
    
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


@router.post("/{order_id}/return", response_model=OrderResponse)
async def request_return(
    order_id: str,
    return_request: ReturnRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Request return for an order (Customer only)"""
    from ....services import order_service
    
    order = order_service.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check if customer owns the order
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this order")
    
    # Check if return already requested or processed (check first before checking delivered)
    if order.status in [OrderStatus.RETURN_REQUESTED, OrderStatus.RETURN_APPROVED, OrderStatus.RETURN_REJECTED, OrderStatus.RETURNED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Return already {order.status.value} for this order"
        )
    
    # Only delivered orders can be returned
    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only delivered orders can be returned"
        )
    
    # Update order to return requested
    order.status = OrderStatus.RETURN_REQUESTED
    order.return_reason = return_request.return_reason
    order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/{order_id}/invoice")
async def download_invoice(
    order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_customer_user)
):
    """Download invoice PDF for a delivered order (Customer only)"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check if customer owns the order
    if order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this order")
    
    # Check if order is delivered
    if order.status != OrderStatus.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice can only be generated for delivered orders"
        )
    
    # Check if invoice file exists
    # Get the backend directory
    backend_dir = Path(__file__).parent.parent.parent.parent.parent
    invoice_dir = backend_dir / "static" / "invoices"
    invoice_file = invoice_dir / f"invoice_{order.order_number}.pdf"
    
    if invoice_file.exists():
        return FileResponse(
            path=str(invoice_file),
            filename=f"invoice_{order.order_number}.pdf",
            media_type="application/pdf"
        )
    
    # Generate invoice on the fly if it doesn't exist
    try:
        from ....utils.invoice import generate_invoice_pdf
        invoice_buffer = generate_invoice_pdf(order, output_path=invoice_dir)
        
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