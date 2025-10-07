from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.category import Category
from ..schemas.category import CategoryCreate, CategoryUpdate
import uuid
import re


def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from category name"""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')


def calculate_level(db: Session, parent_id: Optional[str]) -> int:
    """Calculate category level based on parent"""
    if not parent_id:
        return 1
    
    parent = db.query(Category).filter(Category.id == parent_id).first()
    if not parent:
        return 1
    
    return parent.level + 1


def create_category(db: Session, category: CategoryCreate) -> Category:
    """Create a new category"""
    # Generate unique slug
    base_slug = generate_slug(category.name)
    slug = base_slug
    counter = 1
    
    while db.query(Category).filter(Category.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Calculate level
    level = calculate_level(db, category.parent_id)
    
    # Validate parent exists if provided
    if category.parent_id:
        parent = db.query(Category).filter(Category.id == category.parent_id).first()
        if not parent:
            raise ValueError("Parent category not found")
    
    db_category = Category(
        id=str(uuid.uuid4()),
        name=category.name,
        slug=slug,
        description=category.description,
        parent_id=category.parent_id,
        level=level,
        sort_order=category.sort_order,
        is_active=category.is_active
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


def get_category(db: Session, category_id: str) -> Optional[Category]:
    """Get category by ID"""
    return db.query(Category).filter(Category.id == category_id).first()


def get_category_by_slug(db: Session, slug: str) -> Optional[Category]:
    """Get category by slug"""
    return db.query(Category).filter(Category.slug == slug).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100, parent_id: Optional[str] = None, active_only: bool = True) -> List[Category]:
    """Get categories with optional filtering"""
    query = db.query(Category)
    
    if active_only:
        query = query.filter(Category.is_active == True)
    
    if parent_id is not None:
        query = query.filter(Category.parent_id == parent_id)
    
    return query.order_by(Category.sort_order, Category.name).offset(skip).limit(limit).all()


def get_category_tree(db: Session, parent_id: Optional[str] = None) -> List[Category]:
    """Get hierarchical category tree without duplicates"""
    if parent_id is None:
        # Start from root categories only
        roots = (
            db.query(Category)
            .filter(Category.is_active == True)
            .filter(Category.parent_id == None)
            .order_by(Category.sort_order, Category.name)
            .all()
        )
    else:
        roots = get_categories(db, parent_id=parent_id, limit=1000)

    for root in roots:
        root.children = []
        _build_tree_recursive(db, root)

    return roots


def _build_tree_recursive(db: Session, category: Category):
    """Recursively build category tree"""
    children = get_categories(db, parent_id=category.id, limit=1000)
    for child in children:
        child.children = []
        category.children.append(child)
        _build_tree_recursive(db, child)


def update_category(db: Session, category_id: str, category_update: CategoryUpdate) -> Optional[Category]:
    """Update category"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        return None
    
    update_data = category_update.dict(exclude_unset=True)
    
    # Handle slug regeneration if name changed
    if "name" in update_data:
        base_slug = generate_slug(update_data["name"])
        slug = base_slug
        counter = 1
        
        while db.query(Category).filter(Category.slug == slug, Category.id != category_id).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        update_data["slug"] = slug
    
    # Handle level recalculation if parent changed
    if "parent_id" in update_data:
        if update_data["parent_id"]:
            parent = db.query(Category).filter(Category.id == update_data["parent_id"]).first()
            if not parent:
                raise ValueError("Parent category not found")
            update_data["level"] = parent.level + 1
        else:
            update_data["level"] = 1
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


def delete_category(db: Session, category_id: str) -> bool:
    """Delete category (soft delete by setting is_active=False)"""
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        return False
    
    # Check if category has children
    children = db.query(Category).filter(Category.parent_id == category_id).first()
    if children:
        raise ValueError("Cannot delete category with children")
    
    # Check if category has products
    # This will be implemented when product model is ready
    
    # Soft delete
    db_category.is_active = False
    db.commit()
    
    return True


def get_category_path(db: Session, category_id: str) -> List[Category]:
    """Get full path from root to category"""
    path = []
    current = db.query(Category).filter(Category.id == category_id).first()
    
    while current:
        path.insert(0, current)
        if current.parent_id:
            current = db.query(Category).filter(Category.id == current.parent_id).first()
        else:
            break
    
    return path 