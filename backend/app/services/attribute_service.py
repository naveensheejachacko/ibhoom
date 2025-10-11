from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.attribute import Attribute, AttributeValue, CategoryAttribute
from ..schemas.attribute import (
    AttributeCreate, AttributeUpdate, AttributeValueCreate, 
    AttributeValueUpdate, CategoryAttributeCreate, CategoryAttributeUpdate
)


def create_attribute(db: Session, attribute: AttributeCreate) -> Attribute:
    """Create a new attribute"""
    db_attribute = Attribute(**attribute.dict())
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)
    return db_attribute


def get_attribute(db: Session, attribute_id: str) -> Optional[Attribute]:
    """Get attribute by ID"""
    return db.query(Attribute).filter(Attribute.id == attribute_id).first()


def get_attributes(db: Session, skip: int = 0, limit: int = 100) -> List[Attribute]:
    """Get all attributes"""
    return db.query(Attribute).order_by(Attribute.sort_order).offset(skip).limit(limit).all()


def update_attribute(db: Session, attribute_id: str, attribute_update: AttributeUpdate) -> Optional[Attribute]:
    """Update attribute"""
    db_attribute = get_attribute(db, attribute_id)
    if not db_attribute:
        return None
    
    update_data = attribute_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_attribute, key, value)
    
    db.commit()
    db.refresh(db_attribute)
    return db_attribute


def delete_attribute(db: Session, attribute_id: str) -> bool:
    """Delete attribute"""
    db_attribute = get_attribute(db, attribute_id)
    if not db_attribute:
        return False
    
    db.delete(db_attribute)
    db.commit()
    return True


# Attribute Values
def create_attribute_value(db: Session, attribute_value: AttributeValueCreate) -> AttributeValue:
    """Create a new attribute value"""
    db_attribute_value = AttributeValue(**attribute_value.dict())
    db.add(db_attribute_value)
    db.commit()
    db.refresh(db_attribute_value)
    return db_attribute_value


def get_attribute_value(db: Session, value_id: str) -> Optional[AttributeValue]:
    """Get attribute value by ID"""
    return db.query(AttributeValue).filter(AttributeValue.id == value_id).first()


def get_attribute_values(db: Session, attribute_id: str) -> List[AttributeValue]:
    """Get all values for an attribute"""
    return db.query(AttributeValue).filter(
        AttributeValue.attribute_id == attribute_id
    ).order_by(AttributeValue.sort_order).all()


def update_attribute_value(db: Session, value_id: str, value_update: AttributeValueUpdate) -> Optional[AttributeValue]:
    """Update attribute value"""
    db_value = get_attribute_value(db, value_id)
    if not db_value:
        return None
    
    update_data = value_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_value, key, value)
    
    db.commit()
    db.refresh(db_value)
    return db_value


def delete_attribute_value(db: Session, value_id: str) -> bool:
    """Delete attribute value"""
    db_value = get_attribute_value(db, value_id)
    if not db_value:
        return False
    
    db.delete(db_value)
    db.commit()
    return True


# Category Attributes
def create_category_attribute(db: Session, category_attribute: CategoryAttributeCreate) -> CategoryAttribute:
    """Link an attribute to a category"""
    # Check if already exists
    existing = db.query(CategoryAttribute).filter(
        CategoryAttribute.category_id == category_attribute.category_id,
        CategoryAttribute.attribute_id == category_attribute.attribute_id
    ).first()
    
    if existing:
        raise ValueError("Attribute already linked to this category")
    
    db_category_attribute = CategoryAttribute(**category_attribute.dict())
    db.add(db_category_attribute)
    db.commit()
    db.refresh(db_category_attribute)
    return db_category_attribute


def get_category_attributes(db: Session, category_id: str) -> List[CategoryAttribute]:
    """Get all attributes for a category"""
    return db.query(CategoryAttribute).filter(
        CategoryAttribute.category_id == category_id
    ).all()


def get_category_attribute(db: Session, category_attribute_id: str) -> Optional[CategoryAttribute]:
    """Get category attribute by ID"""
    return db.query(CategoryAttribute).filter(CategoryAttribute.id == category_attribute_id).first()


def update_category_attribute(db: Session, category_attribute_id: str, update: CategoryAttributeUpdate) -> Optional[CategoryAttribute]:
    """Update category attribute relationship"""
    db_category_attribute = get_category_attribute(db, category_attribute_id)
    if not db_category_attribute:
        return None
    
    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category_attribute, key, value)
    
    db.commit()
    db.refresh(db_category_attribute)
    return db_category_attribute


def delete_category_attribute(db: Session, category_attribute_id: str) -> bool:
    """Remove attribute link from category"""
    db_category_attribute = get_category_attribute(db, category_attribute_id)
    if not db_category_attribute:
        return False
    
    db.delete(db_category_attribute)
    db.commit()
    return True

