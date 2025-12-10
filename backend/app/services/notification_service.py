"""
Notification service for creating in-app notifications when orders are placed.
"""
from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

from ..models.notification import Notification, NotificationType
from ..models.order import Order, OrderItem
from ..models.user import User, UserRole
from ..models.product import Product
from ..models.seller import Seller

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for creating and managing in-app notifications"""
    
    @staticmethod
    def create_notification(
        db: Session,
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        order_id: Optional[str] = None
    ) -> Notification:
        """
        Create a new notification in the database.
        
        Args:
            db: Database session
            user_id: User ID to notify (admin or seller)
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            order_id: Related order ID (optional)
            
        Returns:
            Created notification
        """
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            order_id=order_id,
            is_read=False
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        logger.info(f"Created notification {notification.id} for user {user_id}: {title}")
        return notification
    
    @staticmethod
    def notify_admin_new_order(db: Session, order: Order) -> Notification:
        """
        Create notification for admin when a new order is placed.
        
        Args:
            db: Database session
            order: The order that was placed
            
        Returns:
            Created notification
        """
        # Get admin user
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            raise ValueError("Admin user not found")
        
        # Count items
        item_count = len(order.items)
        items_text = f"{item_count} item{'s' if item_count != 1 else ''}"
        
        # Get customer name safely
        customer_name = "Customer"
        if order.customer:
            customer_name = f"{order.customer.first_name or ''} {order.customer.last_name or ''}".strip() or "Customer"
        
        title = f"New Order: {order.order_number}"
        message = f"New order received from {customer_name}. Total: ₹{order.grand_total_amount:.2f} ({items_text})"
        
        return NotificationService.create_notification(
            db=db,
            user_id=admin.id,
            notification_type=NotificationType.NEW_ORDER,
            title=title,
            message=message,
            order_id=order.id
        )
    
    @staticmethod
    def notify_seller_new_order(
        db: Session,
        order: Order,
        seller_user_id: str,
        seller_items: List[OrderItem]
    ) -> Notification:
        """
        Create notification for seller when their product is ordered.
        
        Args:
            db: Database session
            order: The order that was placed
            seller_user_id: Seller's user ID
            seller_items: List of order items belonging to this seller
            
        Returns:
            Created notification
        """
        # Calculate seller's total from their items
        seller_total = sum(float(item.total_seller_amount) for item in seller_items)
        item_count = len(seller_items)
        items_text = f"{item_count} product{'s' if item_count != 1 else ''}"
        
        title = f"New Order for Your Products: {order.order_number}"
        message = f"Your {items_text} ordered. You will receive ₹{seller_total:.2f}. Order: {order.order_number}"
        
        return NotificationService.create_notification(
            db=db,
            user_id=seller_user_id,
            notification_type=NotificationType.NEW_ORDER,
            title=title,
            message=message,
            order_id=order.id
        )
    
    @staticmethod
    def notify_order_placed(db: Session, order: Order) -> dict:
        """
        Create notifications for admin and all sellers when an order is placed.
        This method groups order items by seller and creates individual notifications.
        Also sends Firebase push notifications if enabled.
        
        Args:
            db: Database session
            order: The order that was placed
            
        Returns:
            Dictionary with notification results
        """
        results = {
            "admin_notified": False,
            "admin_fcm_sent": False,
            "sellers_notified": {},
            "sellers_fcm_sent": {},
            "errors": []
        }
        
        try:
            # Ensure we have a clean transaction state
            # Rollback any failed transaction first
            try:
                db.rollback()
            except:
                pass
            
            # Reload order with relationships in a fresh query
            order = db.query(Order).options(
                joinedload(Order.customer),
                joinedload(Order.items)
            ).filter(Order.id == order.id).first()
            
            if not order:
                results["errors"].append("Order not found")
                return results
            
            # Notify admin
            try:
                admin_notification = NotificationService.notify_admin_new_order(db, order)
                results["admin_notified"] = True
                logger.info(f"✅ Admin notification created: {admin_notification.id}")
                
                # Send Firebase push notification to admin (non-blocking)
                # Use a separate try-except to ensure DB notification is created even if FCM fails
                try:
                    from ..services.firebase_service import FirebaseService
                    # Create a new session for FCM to avoid transaction conflicts
                    from ..core.database import SessionLocal
                    fcm_db = SessionLocal()
                    try:
                        fcm_result = FirebaseService.send_to_user(
                            db=fcm_db,
                            user_id=admin_notification.user_id,
                            title=admin_notification.title,
                            body=admin_notification.message,
                            data={
                                "type": admin_notification.notification_type.value,
                                "order_id": str(order.id),
                                "notification_id": str(admin_notification.id)
                            }
                        )
                        if fcm_result.get("success_count", 0) > 0:
                            results["admin_fcm_sent"] = True
                            logger.info(f"Firebase notification sent to admin for order {order.order_number}")
                    finally:
                        fcm_db.close()
                except Exception as fcm_error:
                    # Log but don't fail - DB notification is already created
                    logger.warning(f"Failed to send Firebase notification to admin: {str(fcm_error)}")
                    results["errors"].append(f"Admin FCM error: {str(fcm_error)}")
                    
            except Exception as e:
                error_msg = f"Failed to notify admin: {str(e)}"
                logger.error(error_msg, exc_info=True)
                results["errors"].append(error_msg)
                # Rollback to clean state
                try:
                    db.rollback()
                except:
                    pass
            
            # Group order items by seller
            seller_items_map = {}
            for item in order.items:
                # Get product with seller relationship
                # Use class-bound attributes instead of strings for SQLAlchemy 2.0+
                product = db.query(Product).options(
                    joinedload(Product.seller).joinedload(Seller.user)
                ).filter(Product.id == item.product_id).first()
                
                if not product or not product.seller:
                    logger.warning(f"Product {item.product_id} has no seller, skipping notification")
                    continue
                
                seller_user_id = product.seller.user.id
                
                if seller_user_id not in seller_items_map:
                    seller_items_map[seller_user_id] = []
                
                seller_items_map[seller_user_id].append(item)
            
            # Notify each seller
            for seller_user_id, seller_items in seller_items_map.items():
                try:
                    seller_notification = NotificationService.notify_seller_new_order(
                        db, order, seller_user_id, seller_items
                    )
                    results["sellers_notified"][seller_user_id] = True
                    logger.info(f"✅ Seller notification created for {seller_user_id}: {seller_notification.id}")
                    
                    # Send Firebase push notification to seller (non-blocking)
                    # Use a separate session to avoid transaction conflicts
                    try:
                        from ..services.firebase_service import FirebaseService
                        from ..core.database import SessionLocal
                        fcm_db = SessionLocal()
                        try:
                            fcm_result = FirebaseService.send_to_user(
                                db=fcm_db,
                                user_id=seller_user_id,
                                title=seller_notification.title,
                                body=seller_notification.message,
                                data={
                                    "type": seller_notification.notification_type.value,
                                    "order_id": str(order.id),
                                    "notification_id": str(seller_notification.id)
                                }
                            )
                            if fcm_result.get("success_count", 0) > 0:
                                results["sellers_fcm_sent"][seller_user_id] = True
                                logger.info(f"Firebase notification sent to seller {seller_user_id} for order {order.order_number}")
                        finally:
                            fcm_db.close()
                    except Exception as fcm_error:
                        # Log but don't fail - DB notification is already created
                        logger.warning(f"Failed to send Firebase notification to seller {seller_user_id}: {str(fcm_error)}")
                        results["errors"].append(f"Seller {seller_user_id} FCM error: {str(fcm_error)}")
                        
                except Exception as e:
                    error_msg = f"Failed to notify seller {seller_user_id}: {str(e)}"
                    logger.error(error_msg, exc_info=True)
                    results["errors"].append(error_msg)
                    results["sellers_notified"][seller_user_id] = False
                    # Rollback to clean state
                    try:
                        db.rollback()
                    except:
                        pass
            
        except Exception as e:
            error_msg = f"Error in notify_order_placed: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)
        
        return results
    
    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False
    ) -> List[Notification]:
        """
        Get notifications for a user.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of notifications to skip
            limit: Maximum number of notifications to return
            unread_only: If True, only return unread notifications
            
        Returns:
            List of notifications
        """
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def mark_as_read(db: Session, notification_id: str, user_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            db: Database session
            notification_id: Notification ID
            user_id: User ID (to verify ownership)
            
        Returns:
            True if marked as read, False otherwise
        """
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            return False
        
        notification.is_read = True
        db.commit()
        return True
    
    @staticmethod
    def mark_all_as_read(db: Session, user_id: str) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of notifications marked as read
        """
        count = db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        return count
    
    @staticmethod
    def get_unread_count(db: Session, user_id: str) -> int:
        """
        Get count of unread notifications for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Number of unread notifications
        """
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()
