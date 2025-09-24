from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..core.database import Base


class AttributeType(str, enum.Enum):
    TEXT = "text"
    SELECT = "select"
    MULTISELECT = "multiselect"
    NUMBER = "number"


class Attribute(Base):
    __tablename__ = "attributes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)  # color, size, storage, brand
    type = Column(Enum(AttributeType), nullable=False)
    is_required = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    attribute_values = relationship("AttributeValue", back_populates="attribute")
    category_attributes = relationship("CategoryAttribute", back_populates="attribute")
    product_variant_attributes = relationship("ProductVariantAttribute", back_populates="attribute")
    
    def __repr__(self):
        return f"<Attribute {self.name}>"


class AttributeValue(Base):
    __tablename__ = "attribute_values"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    attribute_id = Column(String, ForeignKey("attributes.id"), nullable=False)
    value = Column(String(255), nullable=False)  # Red, Large, 128GB, Samsung
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    attribute = relationship("Attribute", back_populates="attribute_values")
    product_variant_attributes = relationship("ProductVariantAttribute", back_populates="attribute_value")
    
    def __repr__(self):
        return f"<AttributeValue {self.value}>"


class CategoryAttribute(Base):
    __tablename__ = "category_attributes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    attribute_id = Column(String, ForeignKey("attributes.id"), nullable=False)
    is_required = Column(Boolean, default=False)
    is_variant = Column(Boolean, default=False)  # affects pricing/inventory
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="category_attributes")
    attribute = relationship("Attribute", back_populates="category_attributes")
    
    def __repr__(self):
        return f"<CategoryAttribute {self.category_id}-{self.attribute_id}>" 