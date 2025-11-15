from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from ..models.order import Order, OrderItem, OrderStatus, PaymentStatus
from ..models.product import Product, ProductVariant
from ..models.user import User
from ..models.seller import Seller
from ..schemas.order import OrderCreate, OrderStatusUpdate, PaymentStatusUpdate
from ..core.config import settings
from ..utils.location import geocode_pincode_kerala, haversine_distance
import uuid
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)


def generate_order_number() -> str:
    """Generate a unique order number"""
    timestamp = int(time.time())
    random_suffix = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{random_suffix}"


def create_order(db: Session, order: OrderCreate, customer_id: str) -> Order:
    """Create a new order"""
    # Validate customer exists
    customer = db.query(User).filter(User.id == customer_id).first()
    if not customer:
        raise ValueError("Customer not found")
    
    # Validate and calculate totals
    total_customer_amount = Decimal('0.0')
    total_seller_amount = Decimal('0.0')
    total_commission_amount = Decimal('0.0')
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
        
        # Validate delivery location - check if seller delivers to customer's pincode
        seller = product.seller
        if not seller:
            raise ValueError(f"Product {product.name} has no associated seller")
        
        # Check if seller has location coordinates
        if seller.latitude and seller.longitude:
            # Geocode customer's delivery pincode (cache-first, with retries)
            delivery_coords = None
            for _ in range(3):
                # Avoid DB writes during active order transaction to prevent PendingRollbackError
                delivery_coords = geocode_pincode_kerala(order.delivery_pincode, db_session=None)
                if delivery_coords:
                    break
                time.sleep(0.5)

            if delivery_coords:
                delivery_lat, delivery_lon = delivery_coords
                
                # Calculate distance between seller and delivery location
                distance_km = haversine_distance(
                    seller.latitude, 
                    seller.longitude,
                    delivery_lat,
                    delivery_lon
                )
                
                # Check if within delivery radius
                max_radius = settings.MAX_DELIVERY_RADIUS_KM
                if distance_km > max_radius:
                    raise ValueError(
                        f"Product '{product.name}' from seller '{seller.business_name}' "
                        f"is not available for delivery to pincode {order.delivery_pincode}. "
                        f"Distance: {distance_km:.1f}km (maximum: {max_radius}km). "
                        f"Please select a product from a seller in your area."
                    )
            else:
                # Geocoding failed
                if settings.DELIVERY_VALIDATION_STRICT:
                    raise ValueError(
                        f"Unable to verify delivery location for pincode {order.delivery_pincode}. "
                        f"Please confirm the pincode or try again later."
                    )
                else:
                    # Allow order to proceed in non-strict mode
                    logger.warning(
                        f"Could not geocode delivery pincode {order.delivery_pincode} "
                        f"for order validation. Allowing order to proceed (non-strict mode)."
                    )
        else:
            # If seller doesn't have coordinates, log warning but allow order
            logger.warning(
                f"Seller {seller.business_name} (ID: {seller.id}) does not have location coordinates. "
                f"Delivery location validation skipped."
            )
        
        # Calculate item totals
        total_seller_item = Decimal(str(seller_unit_price)) * item_data.quantity
        total_customer_item = Decimal(str(customer_unit_price)) * item_data.quantity
        total_commission_item = Decimal(str(commission_unit_amount)) * item_data.quantity
        
        total_seller_amount += total_seller_item
        total_customer_amount += total_customer_item
        total_commission_amount += total_commission_item
        
        order_items_data.append({
            'product_id': item_data.product_id,
            'product_variant_id': item_data.product_variant_id,
            'quantity': item_data.quantity,
            'seller_unit_price': Decimal(str(seller_unit_price)),
            'customer_unit_price': Decimal(str(customer_unit_price)),
            'commission_unit_rate': Decimal(str(commission_unit_rate)),
            'commission_unit_amount': Decimal(str(commission_unit_amount)),
            'total_seller_amount': total_seller_item,
            'total_customer_amount': total_customer_item,
            'total_commission_amount': total_commission_item,
            'product_name': product.name
        })
    
    # Create order
    db_order = Order(
        id=str(uuid.uuid4()),
        order_number=generate_order_number(),
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
    
    # Store order ID before any operations that might affect the transaction
    order_id = db_order.id
    order_number = db_order.order_number
    
    # Clear customer's cart after successful order creation
    # Use a separate try-except to ensure it doesn't affect the main transaction
    try:
        from ..services.cart_service import clear_cart
        cleared_count = clear_cart(db, customer_id)
        logger.info(f"Cleared {cleared_count} items from cart for customer {customer_id} after order {order_number}")
    except Exception as e:
        # Log error but don't fail order creation
        logger.warning(f"Failed to clear cart for customer {customer_id} after order {order_number}: {str(e)}")
        # Rollback any partial cart clearing, but order is already committed
        try:
            db.rollback()
        except:
            pass
    
    # Send notifications to admin and sellers (non-blocking)
    # IMPORTANT: Do this in a background task or ensure errors don't affect the session
    try:
        from ..services.notification_service import NotificationService
        notification_results = NotificationService.notify_order_placed(db, db_order)
        if notification_results.get("errors"):
            logger.warning(f"Some notifications failed for order {order_number}: {notification_results['errors']}")
    except Exception as e:
        # Log error but don't fail order creation
        logger.error(f"Failed to send notifications for order {order_number}: {str(e)}")
        # Ensure transaction is rolled back if notification caused issues
        try:
            db.rollback()
        except:
            pass
    
    # Reload order with all relationships in a fresh query to avoid transaction issues
    # This ensures we have a clean session state
    from sqlalchemy.orm import joinedload
    db_order = db.query(Order).options(
        joinedload(Order.items)
    ).filter(Order.id == order_id).first()
    
    if not db_order:
        # If reload fails, raise error - order was created but we can't retrieve it
        raise ValueError(f"Order {order_number} was created but could not be retrieved. Order ID: {order_id}")
    
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
    """Update order status (Admin only) - Legacy method, use update_order_status_admin"""
    return update_order_status_admin(db, order_id, status_update)


def update_order_status_admin(db: Session, order_id: str, status_update: OrderStatusUpdate) -> Optional[Order]:
    """Update order status (Admin only - can set dispatched, delivered, cancelled)"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return None
    
    # Admin can only set specific statuses
    allowed_statuses = [
        OrderStatus.READY_FOR_DISPATCH,  # Admin can also mark as ready for dispatch
        OrderStatus.DISPATCHED,
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED
    ]
    
    if status_update.status not in allowed_statuses:
        raise ValueError(f"Admin can only set status to: {[s.value for s in allowed_statuses]}")
    
    current_status = db_order.status
    
    # Validate status transitions for admin
    # Admin can set ready_for_dispatch from pending or processing
    if status_update.status == OrderStatus.READY_FOR_DISPATCH:
        if current_status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            raise ValueError(f"Can only set ready_for_dispatch from pending or processing status, current: {current_status.value}")
    
    # Admin can dispatch from ready_for_dispatch
    elif status_update.status == OrderStatus.DISPATCHED:
        if current_status != OrderStatus.READY_FOR_DISPATCH:
            raise ValueError(f"Can only dispatch order from ready_for_dispatch status, current: {current_status.value}")
    
    # Admin can mark as delivered from dispatched or ready_for_dispatch
    elif status_update.status == OrderStatus.DELIVERED:
        if current_status not in [OrderStatus.DISPATCHED, OrderStatus.READY_FOR_DISPATCH]:
            raise ValueError(f"Can only mark as delivered from dispatched or ready_for_dispatch status, current: {current_status.value}")
        
        # Generate invoice when order is marked as delivered
        try:
            from ..utils.invoice import generate_invoice_pdf
            from pathlib import Path
            
            # Get the backend directory (parent of app)
            backend_dir = Path(__file__).parent.parent.parent
            invoice_dir = backend_dir / "static" / "invoices"
            invoice_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate and save invoice
            invoice_buffer = generate_invoice_pdf(db_order, output_path=invoice_dir)
        except Exception as e:
            # Log error but don't fail the order status update
            import logging
            logging.error(f"Failed to generate invoice for order {db_order.order_number}: {str(e)}")
    
    # Admin can cancel from pending, processing, ready_for_dispatch
    elif status_update.status == OrderStatus.CANCELLED:
        if current_status not in [OrderStatus.PENDING, OrderStatus.PROCESSING, OrderStatus.READY_FOR_DISPATCH]:
            raise ValueError(f"Cannot cancel order from {current_status.value} status")
        
        # Restore stock when cancelling
        from ..models.product import ProductVariant
        for item in db_order.items:
            if item.product_variant_id:
                variant = db.query(ProductVariant).filter(ProductVariant.id == item.product_variant_id).first()
                if variant:
                    variant.stock_quantity += item.quantity
            else:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.stock_quantity += item.quantity
    
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
    try:
        total_orders = db.query(Order).count()
        pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).count()
        processing_orders = db.query(Order).filter(Order.status == OrderStatus.PROCESSING).count()
        shipped_orders = db.query(Order).filter(Order.status == OrderStatus.DISPATCHED).count()  # Updated to DISPATCHED
        delivered_orders = db.query(Order).filter(Order.status == OrderStatus.DELIVERED).count()
        cancelled_orders = db.query(Order).filter(Order.status == OrderStatus.CANCELLED).count()
        
        # Calculate revenue (from delivered orders only)
        revenue_result = db.query(
            db.func.sum(Order.total_customer_amount),
            db.func.sum(Order.total_commission_amount)
        ).filter(Order.status == OrderStatus.DELIVERED).first()
        
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
    except Exception as e:
        print(f"Error in get_order_stats: {e}")
        # Return default values if there's an error
        return {
            "total_orders": 0,
            "pending_orders": 0,
            "processing_orders": 0,
            "shipped_orders": 0,
            "delivered_orders": 0,
            "cancelled_orders": 0,
            "total_revenue": 0.0,
            "total_commission": 0.0
        }


def cancel_order(db: Session, order_id: str, admin_notes: Optional[str] = None) -> Optional[Order]:
    """Cancel order and restore stock (Admin only)"""
    from ..schemas.order import OrderStatusUpdate
    
    status_update = OrderStatusUpdate(status=OrderStatus.CANCELLED, admin_notes=admin_notes)
    return update_order_status_admin(db, order_id, status_update)


def handle_return(db: Session, order_id: str, return_update) -> Optional[Order]:
    """Handle return request (Admin only - approve, reject, or accept return completion)"""
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        return None
    
    # Only return_requested orders can be processed
    if db_order.status != OrderStatus.RETURN_REQUESTED:
        raise ValueError(f"Can only process return from return_requested status, current: {db_order.status.value}")
    
    # Validate return status
    allowed_return_statuses = [
        OrderStatus.RETURN_APPROVED,
        OrderStatus.RETURN_REJECTED,
        OrderStatus.RETURNED
    ]
    
    if return_update.status not in allowed_return_statuses:
        raise ValueError(f"Admin can only set return status to: {[s.value for s in allowed_return_statuses]}")
    
    # Can approve or reject from return_requested
    if return_update.status in [OrderStatus.RETURN_APPROVED, OrderStatus.RETURN_REJECTED]:
        db_order.status = return_update.status
        if return_update.return_notes:
            db_order.return_notes = return_update.return_notes
    
    # Can mark as returned from return_approved
    elif return_update.status == OrderStatus.RETURNED:
        if db_order.status != OrderStatus.RETURN_APPROVED:
            raise ValueError(f"Can only mark as returned from return_approved status, current: {db_order.status.value}")
        
        db_order.status = OrderStatus.RETURNED
        if return_update.return_notes:
            db_order.return_notes = return_update.return_notes
    
        # Restore stock when return is completed
    for item in db_order.items:
        if item.product_variant_id:
            variant = db.query(ProductVariant).filter(ProductVariant.id == item.product_variant_id).first()
            if variant:
                variant.stock_quantity += item.quantity
        else:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_quantity += item.quantity
    
    db_order.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_order)
    
    return db_order 