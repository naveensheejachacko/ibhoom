"""
Firebase Cloud Messaging (FCM) service for sending push notifications.
"""
import firebase_admin
from firebase_admin import credentials, messaging
from typing import List, Optional, Dict, Any
import logging
import json
import os
from pathlib import Path
from sqlalchemy.orm import Session

from ..core.config import settings

logger = logging.getLogger(__name__)

# Global Firebase app instance
_firebase_app = None


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    if not settings.FIREBASE_ENABLED:
        logger.info("Firebase notifications are disabled")
        return None
    
    try:
        # Option 1: Use service account JSON file
        if settings.FIREBASE_SERVICE_ACCOUNT_PATH:
            cred_path = Path(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
            # Resolve relative paths to absolute paths
            if not cred_path.is_absolute():
                # If relative, resolve from backend directory
                # __file__ is at: backend/app/services/firebase_service.py
                # So parent.parent.parent = backend/
                backend_dir = Path(__file__).parent.parent.parent
                cred_path = (backend_dir / cred_path).resolve()
            else:
                cred_path = cred_path.resolve()
            
            logger.info(f"Attempting to load Firebase credentials from: {cred_path}")
            if cred_path.exists():
                try:
                    cred = credentials.Certificate(str(cred_path))
                    _firebase_app = firebase_admin.initialize_app(cred)
                    logger.info(f"✅ Firebase initialized successfully from: {cred_path}")
                    return _firebase_app
                except Exception as e:
                    logger.error(f"Failed to initialize Firebase with file {cred_path}: {str(e)}")
            else:
                logger.error(f"Firebase service account file not found at: {cred_path}")
        
        # Option 2: Use service account JSON string from environment
        if settings.FIREBASE_SERVICE_ACCOUNT_JSON:
            try:
                service_account_info = json.loads(settings.FIREBASE_SERVICE_ACCOUNT_JSON)
                cred = credentials.Certificate(service_account_info)
                _firebase_app = firebase_admin.initialize_app(cred)
                logger.info("Firebase initialized from JSON string")
                return _firebase_app
            except json.JSONDecodeError as e:
                logger.error(f"Invalid FIREBASE_SERVICE_ACCOUNT_JSON format: {e}")
        
        # Option 3: Use default credentials (for Google Cloud environments)
        try:
            _firebase_app = firebase_admin.initialize_app()
            logger.info("Firebase initialized with default credentials")
            return _firebase_app
        except Exception as e:
            logger.warning(f"Failed to initialize Firebase with default credentials: {e}")
        
        logger.error("Firebase initialization failed: No valid credentials found")
        return None
        
    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        return None


def get_firebase_app():
    """Get or initialize Firebase app"""
    if _firebase_app is None:
        return initialize_firebase()
    return _firebase_app


class FirebaseService:
    """Service for sending Firebase Cloud Messaging (FCM) push notifications"""
    
    @staticmethod
    def send_notification(
        token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> bool:
        """
        Send a push notification to a single device.
        
        Args:
            token: FCM device token
            title: Notification title
            body: Notification body/message
            data: Optional data payload (key-value pairs)
            image_url: Optional image URL for notification
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not settings.FIREBASE_ENABLED:
            logger.info(f"Firebase disabled. Would send notification to {token[:20]}...")
            return False
        
        app = get_firebase_app()
        if not app:
            logger.error("Firebase not initialized")
            return False
        
        try:
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url
            )
            
            # Build message
            message = messaging.Message(
                notification=notification,
                data=data or {},
                token=token,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='order_notifications'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            
            # Send message
            response = messaging.send(message, app=app)
            logger.info(f"Successfully sent FCM notification: {response}")
            return True
            
        except messaging.UnregisteredError:
            logger.warning(f"FCM token is unregistered: {token[:20]}...")
            return False
        except Exception as e:
            logger.error(f"Failed to send FCM notification: {str(e)}")
            return False
    
    @staticmethod
    def send_multicast_notification(
        tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send push notification to multiple devices.
        
        Args:
            tokens: List of FCM device tokens
            title: Notification title
            body: Notification body/message
            data: Optional data payload
            image_url: Optional image URL
            
        Returns:
            Dictionary with success/failure counts
        """
        if not settings.FIREBASE_ENABLED:
            logger.info(f"Firebase disabled. Would send to {len(tokens)} devices")
            return {"success_count": 0, "failure_count": len(tokens)}
        
        if not tokens:
            return {"success_count": 0, "failure_count": 0}
        
        app = get_firebase_app()
        if not app:
            logger.error("Firebase not initialized")
            return {"success_count": 0, "failure_count": len(tokens)}
        
        try:
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url
            )
            
            # Build multicast message
            message = messaging.MulticastMessage(
                notification=notification,
                data=data or {},
                tokens=tokens,
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        sound='default',
                        channel_id='order_notifications'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1
                        )
                    )
                )
            )
            
            # Send multicast message
            response = messaging.send_multicast(message, app=app)
            
            result = {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": []
            }
            
            # Log failures
            for idx, resp in enumerate(response.responses):
                if not resp.success:
                    logger.warning(f"Failed to send to token {tokens[idx][:20]}...: {resp.exception}")
                    result["responses"].append({
                        "token": tokens[idx],
                        "success": False,
                        "error": str(resp.exception) if resp.exception else "Unknown error"
                    })
                else:
                    result["responses"].append({
                        "token": tokens[idx],
                        "success": True
                    })
            
            logger.info(f"Sent FCM multicast: {response.success_count} success, {response.failure_count} failures")
            return result
            
        except Exception as e:
            logger.error(f"Failed to send FCM multicast notification: {str(e)}")
            return {"success_count": 0, "failure_count": len(tokens), "error": str(e)}
    
    @staticmethod
    def send_to_user(
        db: Session,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send notification to all active devices of a user.
        
        Args:
            db: Database session
            user_id: User ID
            title: Notification title
            body: Notification body
            data: Optional data payload
            image_url: Optional image URL
            
        Returns:
            Dictionary with send results
        """
        try:
            from ..models.fcm_token import FCMToken
        except ImportError:
            logger.warning("FCMToken model not available")
            return {"success_count": 0, "failure_count": 0, "message": "FCM tokens not configured"}
        
        try:
            # Check if table exists by attempting to query
            # If table doesn't exist, this will raise an exception
            tokens = db.query(FCMToken.token).filter(
                FCMToken.user_id == user_id,
                FCMToken.is_active == True
            ).all()
            
            if not tokens:
                logger.info(f"No active FCM tokens found for user {user_id}")
                return {"success_count": 0, "failure_count": 0, "message": "No active tokens"}
            
            token_list = [token[0] for token in tokens]
            
            # Update last_used_at for tokens (in a separate transaction to avoid affecting main transaction)
            try:
                from datetime import datetime
                db.query(FCMToken).filter(
                    FCMToken.user_id == user_id,
                    FCMToken.is_active == True
                ).update({"last_used_at": datetime.utcnow()})
                db.commit()
            except Exception as update_error:
                # Rollback the update if it fails, but don't fail the whole operation
                db.rollback()
                logger.warning(f"Failed to update FCM token last_used_at: {update_error}")
            
            return FirebaseService.send_multicast_notification(
                tokens=token_list,
                title=title,
                body=body,
                data=data,
                image_url=image_url
            )
        except Exception as e:
            # Handle case where fcm_tokens table doesn't exist or other DB errors
            error_msg = str(e)
            if "does not exist" in error_msg or "UndefinedTable" in error_msg:
                logger.warning(f"FCM tokens table does not exist. Run migration to create it. Error: {error_msg}")
                return {"success_count": 0, "failure_count": 0, "message": "FCM tokens table not created yet"}
            else:
                logger.error(f"Error querying FCM tokens: {error_msg}")
                return {"success_count": 0, "failure_count": 0, "message": f"Error: {error_msg}"}

