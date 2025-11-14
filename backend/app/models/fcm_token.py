from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from ..core.database import Base


class FCMToken(Base):
    __tablename__ = "fcm_tokens"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(500), nullable=False, unique=True, index=True)  # FCM device token
    device_type = Column(String(50))  # 'web', 'android', 'ios'
    device_id = Column(String(255))  # Optional device identifier
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow)  # Track when token was last used
    
    # Relationships
    user = relationship("User", back_populates="fcm_tokens")
    
    def __repr__(self):
        return f"<FCMToken {self.user_id} - {self.device_type}>"

