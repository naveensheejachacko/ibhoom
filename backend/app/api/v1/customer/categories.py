from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from ....core.database import get_db
from ....core.dependencies import get_current_user
from ....models.user import User
from ....models.category import Category
from ....models.attribute import CategoryAttribute, Attribute, AttributeValue

router = APIRouter()


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



