from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ..models.product import Product, ProductVariant
from ..models.user import User
from ..schemas.order import OrderCreate, OrderStatusUpdate, PaymentStatusUpdate
import uuid
from datetime import datetime


def create_order(db: Session, order: OrderCreate, customer_id: str) -> Order:
    """Create a new order"""
    # Validate customer exists
    customer = db.query(User).filter(User.id == customer_id).first()
    if not customer:
        raise ValueError("Customer not found")
    
    # Validate and calculate totals
    total_customer_amount = 0.0
    total_seller_amount = 0.0
    total_commission_amount = 0.0
    order_items_data = []
    
    for item_data in order.items:
        # Get product or variant
        if item_data.product_variant_id:
            variant = db.query(ProductVariant).filter(ProductVariant.id == item_data.product_variant_id).first()
            if not variant:
                raise ValueError(f"Product variant {item_data.product_variant_id} not found")
            
            product = variant.product
            seller_unit_price = variant.seller_price
            customer_unit_price = variant.customer_price
            commission_unit_rate = variant.commission_rate
            commission_unit_amount = variant.commission_amount
            
            # Check stock
            if variant.stock_quantity < item_data.quantity:
                raise ValueError(f"Insufficient stock for variant {variant.id}")
            
        else:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise ValueError(f"Product {item_data.product_id} not found")
            
            seller_unit_price = product.seller_price
            customer_unit_price = product.customer_price
            commission_unit_rate = product.commission_rate
            commission_unit_amount = product.commission_amount
            
            # Check stock
            if product.stock_quantity < item_data.quantity:
                raise ValueError(f"Insufficient stock for product {product.id}")
        
        # Check if product is approved
        if product.status != "approved":
            raise ValueError(f"Product {product.name} is not available for purchase")
        
        # Calculate item totals
        total_seller_item = seller_unit_price * item_data.quantity
        total_customer_item = customer_unit_price * item_data.quantity
        total_commission_item = commission_unit_amount * item_data.quantity
        
        total_seller_amount += total_seller_item
        total_customer_amount += total_customer_item
        total_commission_amount += total_commission_item
        
        order_items_data.append({
            'product_id': item_data.product_id,
            'product_variant_id': item_data.product_variant_id,
            'quantity': item_data.quantity,
            'seller_unit_price': seller_unit_price,
            'customer_unit_price': customer_unit_price,
            'commission_unit_rate': commission_unit_rate,
            'commission_unit_amount': commission_unit_amount,
            'total_seller_amount': total_seller_item,
            'total_customer_amount': total_customer_item,
            'total_commission_amount': total_commission_item,
            'product_name': product.name
        })
    
    # Create order
    db_order = Order(
        id=str(uuid.uuid4()),
        customer_id=customer_id,
        total_customer_amount=total_customer_amount,
        total_seller_amount=total_seller_amount,
        total_commission_amount=total_commission_amount,
        delivery_address=order.delivery_address,
        delivery_city=order.delivery_city,
        delivery_state=order.delivery_state,
        delivery_pincode=order.delivery_pincode,
        phone=order.phone,
        notes=order.notes,
        status=OrderStatus.PENDING,
        payment_status=PaymentStatus.COD_PENDING
    )
    
    db.add(db_order)
    db.flush()  # Get the ID
    
    # Create order items
    for item_data in order_items_data:
        order_item = OrderItem(
            id=str(uuid.uuid4()),
            order_id=db_order.id,
            **item_data
        )
        db.add(order_item)
    
    # Update stock quantities
    for item_data in order.items:
        if item_data.product_variant_id:
            variant = db.query(ProductVariant).filter(ProductVariant.id == item_data.product_variant_id).first()
            variant.stock_quantity -= item_data.quantity
        else:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            product.stock_quantity -= item_data.quantity
    
    db.commit()
    db.refresh(db_order)
    
    return db_order


def get_order(db: Session, order_id: str) -> Optional[Order]:
    """Get order by ID"""
    return db.query(Order).filter(Order.id == order_id).first()


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    payment_status: Optional[PaymentStatus] = None
) -> List[Order]:
    """Get orders with filtering"""
    query = db.query(Order)
    
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    if payment_status:
        query = query.filter(Order.payment_status == payment_status)
    
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def update_order_status(db: Session, order_id: str, status_update: OrderStatusUpdate) -> Optional[Order]:
    """Update order status (Admin only)"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return None
    
    db_order.status = status_update.status
    if status_update.admin_notes:
        db_order.admin_notes = status_update.admin_notes
    db_order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_order)
    
    return db_order


def update_payment_status(db: Session, order_id: str, payment_update: PaymentStatusUpdate) -> Optional[Order]:
    """Update payment status (Admin only)"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return None
    
    db_order.payment_status = payment_update.payment_status
    if payment_update.admin_notes:
        db_order.admin_notes = payment_update.admin_notes
    db_order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_order)
    
    return db_order


def get_pending_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get pending orders (Admin only)"""
    return db.query(Order).filter(
        Order.status == OrderStatus.PENDING
    ).order_by(Order.created_at.asc()).offset(skip).limit(limit).all()


def get_order_stats(db: Session) -> dict:
    """Get order statistics (Admin only)"""
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
    processing_orders = db.query(Order).filter(Order.status == OrderStatus.PROCESSING).count()
    shipped_orders = db.query(Order).filter(Order.status == OrderStatus.SHIPPED).count()
    delivered_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).count()
    cancelled_orders = db.query(Order).filter(Order.status == OrderStatus.CANCELLED).count()
    
    # Calculate revenue
    revenue_result = db.query(
        db.func.sum(Order.total_customer_amount),
        db.func.sum(Order.total_commission_amount)
    ).filter(Order.status.in_([OrderStatus.DELIVERED, OrderStatus.SHIPPED])).first()
    
    total_revenue = float(revenue_result[0] or 0)
    total_commission = float(revenue_result[1] or 0)
    
    return {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "processing_orders": processing_orders,
        "shipped_orders": shipped_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,
        "total_revenue": total_revenue,
        "total_commission": total_commission
    }


def cancel_order(db: Session, order_id: str, admin_notes: Optional[str] = None) -> Optional[Order]:
    """Cancel order and restore stock (Admin only)"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return None
    
    # Only allow cancellation for pending/processing orders
    if db_order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
        raise ValueError("Cannot cancel order in current status")
    
    # Restore stock quantities
    for item in db_order.items:
        if item.product_variant_id:
            variant = db.query(ProductVariant).filter(ProductVariant.id == item.product_variant_id).first()
            if variant:
                variant.stock_quantity += item.quantity
        else:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_quantity += item.quantity
    
    # Update order status
    db_order.status = OrderStatus.CANCELLED
    if admin_notes:
        db_order.admin_notes = admin_notes
    db_order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_order)
    
    return db_order 