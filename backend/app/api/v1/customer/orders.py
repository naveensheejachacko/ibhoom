from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from ....core.database import get_db
from ....core.dependencies import get_customer_user
from ....models.user import User
from ....models.order import Order, OrderStatus, PaymentStatus
from ....schemas.order import OrderCreate, OrderResponse, OrderListResponse, ReturnRequest
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