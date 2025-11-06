"""
Pincode geocoding cache model
"""
from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime
from ..core.database import Base


class PincodeCache(Base):
    """Cache for geocoded pincodes"""
    __tablename__ = "pincode_cache"
    
    pincode = Column(String(10), primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    district = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="India")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PincodeCache {self.pincode} -> ({self.latitude}, {self.longitude})>"

















