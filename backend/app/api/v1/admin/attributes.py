from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....models.user import User
from ....schemas.attribute import (
    AttributeCreate, AttributeUpdate, AttributeResponse,
    AttributeValueCreate, AttributeValueUpdate, AttributeValueResponse,
    CategoryAttributeCreate, CategoryAttributeUpdate, CategoryAttributeResponse,
    CategoryAttributesResponse
)
from ....services import attribute_service

router = APIRouter()


# Attributes
@router.post("/", response_model=AttributeResponse, status_code=status.HTTP_201_CREATED)
async def create_attribute(
    attribute: AttributeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new attribute (Admin only)"""
    try:
        db_attribute = attribute_service.create_attribute(db, attribute)
        return db_attribute
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[AttributeResponse])
async def get_attributes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all attributes (Admin only)"""
    attributes = attribute_service.get_attributes(db, skip=skip, limit=limit)
    return attributes


@router.get("/{attribute_id}", response_model=AttributeResponse)
async def get_attribute(
    attribute_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get attribute by ID (Admin only)"""
    attribute = attribute_service.get_attribute(db, attribute_id)
    if not attribute:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
    return attribute


@router.put("/{attribute_id}", response_model=AttributeResponse)
async def update_attribute(
    attribute_id: str,
    attribute_update: AttributeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update attribute (Admin only)"""
    try:
        updated_attribute = attribute_service.update_attribute(db, attribute_id, attribute_update)
        if not updated_attribute:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
        return updated_attribute
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{attribute_id}")
async def delete_attribute(
    attribute_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete attribute (Admin only)"""
    try:
        deleted = attribute_service.delete_attribute(db, attribute_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute not found")
        return {"message": "Attribute deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Attribute Values
@router.post("/values", response_model=AttributeValueResponse, status_code=status.HTTP_201_CREATED)
async def create_attribute_value(
    attribute_value: AttributeValueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new attribute value (Admin only)"""
    try:
        db_value = attribute_service.create_attribute_value(db, attribute_value)
        return db_value
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{attribute_id}/values", response_model=List[AttributeValueResponse])
async def get_attribute_values(
    attribute_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all values for an attribute (Admin only)"""
    values = attribute_service.get_attribute_values(db, attribute_id)
    return values


@router.put("/values/{value_id}", response_model=AttributeValueResponse)
async def update_attribute_value(
    value_id: str,
    value_update: AttributeValueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update attribute value (Admin only)"""
    try:
        updated_value = attribute_service.update_attribute_value(db, value_id, value_update)
        if not updated_value:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute value not found")
        return updated_value
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/values/{value_id}")
async def delete_attribute_value(
    value_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete attribute value (Admin only)"""
    try:
        deleted = attribute_service.delete_attribute_value(db, value_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attribute value not found")
        return {"message": "Attribute value deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Category Attributes
@router.post("/category-attributes", response_model=CategoryAttributeResponse, status_code=status.HTTP_201_CREATED)
async def create_category_attribute(
    category_attribute: CategoryAttributeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Link an attribute to a category (Admin only)"""
    try:
        db_category_attribute = attribute_service.create_category_attribute(db, category_attribute)
        return db_category_attribute
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/category-attributes/{category_id}", response_model=List[CategoryAttributeResponse])
async def get_category_attributes(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all attributes for a category (Admin only)"""
    category_attributes = attribute_service.get_category_attributes(db, category_id)
    return category_attributes


@router.put("/category-attributes/{category_attribute_id}", response_model=CategoryAttributeResponse)
async def update_category_attribute(
    category_attribute_id: str,
    update: CategoryAttributeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update category attribute relationship (Admin only)"""
    try:
        updated = attribute_service.update_category_attribute(db, category_attribute_id, update)
        if not updated:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category attribute not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/category-attributes/{category_attribute_id}")
async def delete_category_attribute(
    category_attribute_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Remove attribute link from category (Admin only)"""
    try:
        deleted = attribute_service.delete_category_attribute(db, category_attribute_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category attribute not found")
        return {"message": "Category attribute deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

