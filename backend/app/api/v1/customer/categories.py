from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ....core.database import get_db
from ....core.dependencies import get_current_user
from ....models.user import User
from ....models.category import Category
from ....models.attribute import CategoryAttribute, Attribute, AttributeValue
from ....schemas.category import CategoryResponse, CategoryWithChildren
from ....services import category_service

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    parent_id: Optional[str] = Query(None, description="Filter by parent category ID"),
    db: Session = Depends(get_db)
):
    """Get all active categories (public endpoint, no auth required)
    
    Returns a flat list of active categories. Use parent_id to filter by parent category.
    For hierarchical tree structure with children, use /tree endpoint.
    """
    categories = category_service.get_categories(
        db, 
        skip=0, 
        limit=1000, 
        parent_id=parent_id, 
        active_only=True
    )
    return categories


@router.get("/tree", response_model=List[CategoryWithChildren])
async def get_category_tree(
    parent_id: Optional[str] = Query(None, description="Get tree starting from specific parent category"),
    db: Session = Depends(get_db)
):
    """Get hierarchical category tree with all children (public endpoint, no auth required)
    
    Returns a tree structure where each category includes its children recursively.
    If parent_id is provided, returns tree starting from that category.
    If parent_id is None, returns all root categories with their children.
    """
    categories = category_service.get_category_tree(db, parent_id)
    return categories


@router.get("/{category_id}/attributes")
async def get_category_attributes(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Return attributes applicable to a category, including values and variant flags.
    
    Accessible by: Customers, Sellers (for product creation), and Admins.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    cat_attrs: List[CategoryAttribute] = (
        db.query(CategoryAttribute)
        .filter(CategoryAttribute.category_id == category_id)
        .all()
    )

    attributes: List[Dict[str, Any]] = []
    for ca in cat_attrs:
        attr: Attribute = db.query(Attribute).filter(Attribute.id == ca.attribute_id).first()
        if not attr:
            continue
        values: List[AttributeValue] = (
            db.query(AttributeValue)
            .filter(AttributeValue.attribute_id == attr.id)
            .order_by(AttributeValue.sort_order)
            .all()
        )
        attributes.append({
            "attribute_id": attr.id,
            "name": attr.name,
            "type": attr.type,
            "is_required": ca.is_required or attr.is_required,
            "is_variant": ca.is_variant,
            "values": [{"id": v.id, "value": v.value} for v in values],
        })

    return {"category_id": category_id, "attributes": attributes}



