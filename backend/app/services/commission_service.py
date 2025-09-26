from sqlalchemy.orm import Session
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from ..models.commission import CommissionSetting, CommissionType
from ..models.category import Category
from ..schemas.commission import CommissionSettingCreate, CommissionSettingUpdate, CommissionCalculation
import uuid


def get_commission_rate(db: Session, category_id: str, product_id: Optional[str] = None, seller_price: float = 0) -> float:
    """Get applicable commission rate based on priority:
    1. Product-specific commission
    2. Category commission
    3. Global commission
    """
    current_time = datetime.utcnow()
    
    # 1. Check for product-specific commission
    if product_id:
        product_commission = db.query(CommissionSetting).filter(
            CommissionSetting.type == CommissionType.PRODUCT,
            CommissionSetting.entity_id == product_id,
            CommissionSetting.is_active == True,
            CommissionSetting.effective_from <= current_time,
            (CommissionSetting.effective_until.is_(None) | 
             (CommissionSetting.effective_until >= current_time)),
            CommissionSetting.min_seller_price <= seller_price,
            (CommissionSetting.max_seller_price.is_(None) | 
             (CommissionSetting.max_seller_price >= seller_price))
        ).first()
        
        if product_commission:
            return float(product_commission.commission_rate)
    
    # 2. Check for category commission (walk up the category tree)
    category = db.query(Category).filter(Category.id == category_id).first()
    while category:
        category_commission = db.query(CommissionSetting).filter(
            CommissionSetting.type == CommissionType.CATEGORY,
            CommissionSetting.entity_id == category.id,
            CommissionSetting.is_active == True,
            CommissionSetting.effective_from <= current_time,
            (CommissionSetting.effective_until.is_(None) | 
             (CommissionSetting.effective_until >= current_time)),
            CommissionSetting.min_seller_price <= seller_price,
            (CommissionSetting.max_seller_price.is_(None) | 
             (CommissionSetting.max_seller_price >= seller_price))
        ).first()
        
        if category_commission:
            return float(category_commission.commission_rate)
        
        # Move to parent category
        if category.parent_id:
            category = db.query(Category).filter(Category.id == category.parent_id).first()
        else:
            break
    
    # 3. Get global commission
    global_commission = db.query(CommissionSetting).filter(
        CommissionSetting.type == CommissionType.GLOBAL,
        CommissionSetting.is_active == True,
        CommissionSetting.effective_from <= current_time,
        (CommissionSetting.effective_until.is_(None) | 
         (CommissionSetting.effective_until >= current_time)),
        CommissionSetting.min_seller_price <= seller_price,
        (CommissionSetting.max_seller_price.is_(None) | 
         (CommissionSetting.max_seller_price >= seller_price))
    ).first()
    
    if global_commission:
        return float(global_commission.commission_rate)
    
    # Default fallback
    return 8.0  # 8% default


def calculate_commission(seller_price: float, commission_rate: float) -> CommissionCalculation:
    """Calculate commission amounts"""
    seller_price_decimal = Decimal(str(seller_price))
    commission_rate_decimal = Decimal(str(commission_rate))
    
    commission_amount = seller_price_decimal * (commission_rate_decimal / 100)
    customer_price = seller_price_decimal + commission_amount
    
    return CommissionCalculation(
        seller_price=float(seller_price_decimal),
        commission_rate=float(commission_rate_decimal),
        commission_amount=float(commission_amount),
        customer_price=float(customer_price)
    )


def create_commission_setting(db: Session, commission: CommissionSettingCreate) -> CommissionSetting:
    """Create a new commission setting"""
    # Validate entity exists if provided
    if commission.entity_id:
        if commission.type == CommissionType.CATEGORY:
            category = db.query(Category).filter(Category.id == commission.entity_id).first()
            if not category:
                raise ValueError("Category not found")
        # Add product validation when product model is ready
    
    # Set default effective_from if not provided
    if not commission.effective_from:
        commission.effective_from = datetime.utcnow()
    
    db_commission = CommissionSetting(
        id=str(uuid.uuid4()),
        type=commission.type,
        entity_id=commission.entity_id,
        commission_rate=commission.commission_rate,
        min_seller_price=commission.min_seller_price,
        max_seller_price=commission.max_seller_price,
        is_active=commission.is_active,
        effective_from=commission.effective_from,
        effective_until=commission.effective_until
    )
    
    db.add(db_commission)
    db.commit()
    db.refresh(db_commission)
    
    return db_commission


def get_commission_setting(db: Session, commission_id: str) -> Optional[CommissionSetting]:
    """Get commission setting by ID"""
    return db.query(CommissionSetting).filter(CommissionSetting.id == commission_id).first()


def get_commission_settings(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    commission_type: Optional[CommissionType] = None,
    active_only: bool = True
) -> List[CommissionSetting]:
    """Get commission settings with filtering"""
    query = db.query(CommissionSetting)
    
    if active_only:
        query = query.filter(CommissionSetting.is_active == True)
    
    if commission_type:
        query = query.filter(CommissionSetting.type == commission_type)
    
    return query.order_by(CommissionSetting.created_at.desc()).offset(skip).limit(limit).all()


def update_commission_setting(
    db: Session, 
    commission_id: str, 
    commission_update: CommissionSettingUpdate
) -> Optional[CommissionSetting]:
    """Update commission setting"""
    db_commission = db.query(CommissionSetting).filter(CommissionSetting.id == commission_id).first()
    if not db_commission:
        return None
    
    update_data = commission_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_commission, field, value)
    
    db.commit()
    db.refresh(db_commission)
    
    return db_commission


def delete_commission_setting(db: Session, commission_id: str) -> bool:
    """Delete commission setting (soft delete)"""
    db_commission = db.query(CommissionSetting).filter(CommissionSetting.id == commission_id).first()
    if not db_commission:
        return False
    
    # Soft delete
    db_commission.is_active = False
    db.commit()
    
    return True


def get_global_commission_rate(db: Session) -> float:
    """Get current global commission rate"""
    global_commission = db.query(CommissionSetting).filter(
        CommissionSetting.type == CommissionType.GLOBAL,
        CommissionSetting.is_active == True
    ).first()
    
    return float(global_commission.commission_rate) if global_commission else 8.0 