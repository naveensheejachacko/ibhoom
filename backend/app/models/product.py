from sqlalchemy import Column, String, Text, DECIMAL, Boolean, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from ..core.database import Base


class ProductStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    HIDDEN = "hidden"


class Product(Base):
    __tablename__ = "products"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    seller_id = Column(String, ForeignKey("sellers.id"), nullable=False)
    category_id = Column(String, ForeignKey("categories.id"), nullable=False)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True)
    description = Column(Text)
    short_description = Column(String(500))
    sku = Column(String(100), unique=True, index=True)
    seller_price = Column(DECIMAL(10, 2), nullable=False)  # Price seller gets
    commission_rate = Column(DECIMAL(5, 2), nullable=False)  # Commission % for this product
    commission_amount = Column(DECIMAL(10, 2), nullable=False)  # Calculated commission
    customer_price = Column(DECIMAL(10, 2), nullable=False)  # Final price customer pays
    stock_quantity = Column(Integer, default=0)
    status = Column(Enum(ProductStatus), default=ProductStatus.DRAFT)
    approval_date = Column(DateTime)
    rejection_reason = Column(Text)
    is_active = Column(Boolean, default=True)
    meta_title = Column(String(255))
    meta_description = Column(String(500))
    tags = Column(Text)  # JSON string for SQLite compatibility
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    seller = relationship("Seller", back_populates="products")
    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product")
    images = relationship("ProductImage", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("ProductReview", back_populates="product")
    
    def __repr__(self):
        return f"<Product {self.name}>"


class ProductVariant(Base):
    __tablename__ = "product_variants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    variant_name = Column(String(255))  # "Red Large", "128GB Black"
    sku = Column(String(100), unique=True, index=True)
    seller_price = Column(DECIMAL(10, 2), nullable=False)  # Price seller gets for this variant
    commission_rate = Column(DECIMAL(5, 2), nullable=False)  # Commission % for this variant
    commission_amount = Column(DECIMAL(10, 2), nullable=False)  # Calculated commission
    customer_price = Column(DECIMAL(10, 2), nullable=False)  # Final price customer pays
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    attributes = relationship("ProductVariantAttribute", back_populates="variant")
    images = relationship("ProductImage", back_populates="variant")
    order_items = relationship("OrderItem", back_populates="variant")
    
    def __repr__(self):
        return f"<ProductVariant {self.variant_name}>"


class ProductVariantAttribute(Base):
    __tablename__ = "product_variant_attributes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    variant_id = Column(String, ForeignKey("product_variants.id"), nullable=False)
    attribute_id = Column(String, ForeignKey("attributes.id"), nullable=False)
    attribute_value_id = Column(String, ForeignKey("attribute_values.id"))
    custom_value = Column(String(255))  # For text inputs
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    variant = relationship("ProductVariant", back_populates="attributes")
    attribute = relationship("Attribute", back_populates="product_variant_attributes")
    attribute_value = relationship("AttributeValue", back_populates="product_variant_attributes")
    
    def __repr__(self):
        return f"<ProductVariantAttribute {self.variant_id}-{self.attribute_id}>"


class ProductImage(Base):
    __tablename__ = "product_images"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String, ForeignKey("products.id"), nullable=False)
    variant_id = Column(String, ForeignKey("product_variants.id"))
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(255))
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="images")
    variant = relationship("ProductVariant", back_populates="images")
    
    def __repr__(self):
        return f"<ProductImage {self.image_url}>" 