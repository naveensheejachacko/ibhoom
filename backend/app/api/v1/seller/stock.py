from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_seller_user
from ....models.user import User
from ....models.product import Product, ProductVariant, ProductStatus
from ....schemas.stock import (
    StockUpdateRequest,
    VariantStockUpdateRequest,
    BulkStockUpdateRequest,
    StockItemResponse
)
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=List[StockItemResponse])
async def get_stock_inventory(
    low_stock_only: bool = Query(False, description="Filter to show only low stock items"),
    search: Optional[str] = Query(None, description="Search by product name or SKU"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Get stock inventory for all seller's products and variants"""
    
    # Get all approved products for this seller
    query = db.query(Product).filter(
        Product.seller_id == current_user.seller.id,
        Product.status != ProductStatus.HIDDEN
    )
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            Product.name.ilike(search_term) | 
            Product.sku.ilike(search_term) if Product.sku else False
        )
    
    products = query.order_by(Product.name).all()
    
    stock_items = []
    low_stock_threshold = 10  # Can be made configurable per product later
    
    for product in products:
        # If product has variants, list each variant separately
        if product.variants and len(product.variants) > 0:
            for variant in product.variants:
                if not variant.is_active:
                    continue
                    
                is_low_stock = variant.stock_quantity <= low_stock_threshold
                
                # Apply low stock filter
                if low_stock_only and not is_low_stock:
                    continue
                
                stock_items.append(StockItemResponse(
                    product_id=product.id,
                    product_name=product.name,
                    product_slug=product.slug,
                    sku=product.sku if hasattr(product, 'sku') else None,
                    variant_id=variant.id,
                    variant_name=variant.variant_name,
                    variant_sku=variant.sku,
                    stock_quantity=variant.stock_quantity,
                    low_stock_threshold=low_stock_threshold,
                    is_low_stock=is_low_stock,
                    status=product.status.value
                ))
        else:
            # Product without variants
            is_low_stock = product.stock_quantity <= low_stock_threshold
            
            # Apply low stock filter
            if low_stock_only and not is_low_stock:
                continue
            
            stock_items.append(StockItemResponse(
                product_id=product.id,
                product_name=product.name,
                product_slug=product.slug,
                sku=product.sku if hasattr(product, 'sku') else None,
                variant_id=None,
                variant_name=None,
                variant_sku=None,
                stock_quantity=product.stock_quantity,
                low_stock_threshold=low_stock_threshold,
                is_low_stock=is_low_stock,
                status=product.status.value
            ))
    
    return stock_items


@router.put("/product/{product_id}")
async def update_product_stock(
    product_id: str,
    stock_update: StockUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Update stock quantity for a product (without variants)"""
    
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Verify seller owns the product
    if product.seller_id != current_user.seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this product"
        )
    
    # Check if product has variants - shouldn't update base product stock if it does
    if product.variants and len(product.variants) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This product has variants. Please update stock for individual variants."
        )
    
    # Update stock
    old_stock = product.stock_quantity
    product.stock_quantity = stock_update.stock_quantity
    product.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(product)
    
    return {
        "message": "Stock updated successfully",
        "product_id": product.id,
        "product_name": product.name,
        "old_stock": old_stock,
        "new_stock": product.stock_quantity
    }


@router.put("/variant/{variant_id}")
async def update_variant_stock(
    variant_id: str,
    stock_update: StockUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Update stock quantity for a product variant"""
    
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()
    
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product variant not found"
        )
    
    # Verify seller owns the product
    if variant.product.seller_id != current_user.seller.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this variant"
        )
    
    # Update stock
    old_stock = variant.stock_quantity
    variant.stock_quantity = stock_update.stock_quantity
    variant.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(variant)
    
    return {
        "message": "Variant stock updated successfully",
        "variant_id": variant.id,
        "variant_name": variant.variant_name,
        "product_name": variant.product.name,
        "old_stock": old_stock,
        "new_stock": variant.stock_quantity
    }


@router.post("/bulk-update")
async def bulk_update_stock(
    bulk_update: BulkStockUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Bulk update stock quantities for multiple variants"""
    
    updated_items = []
    errors = []
    
    for update in bulk_update.updates:
        try:
            variant = db.query(ProductVariant).filter(
                ProductVariant.id == update.variant_id
            ).first()
            
            if not variant:
                errors.append({
                    "variant_id": update.variant_id,
                    "error": "Variant not found"
                })
                continue
            
            # Verify seller owns the product
            if variant.product.seller_id != current_user.seller.id:
                errors.append({
                    "variant_id": update.variant_id,
                    "error": "Not authorized"
                })
                continue
            
            # Update stock
            old_stock = variant.stock_quantity
            variant.stock_quantity = update.stock_quantity
            variant.updated_at = datetime.utcnow()
            
            updated_items.append({
                "variant_id": variant.id,
                "variant_name": variant.variant_name,
                "product_name": variant.product.name,
                "old_stock": old_stock,
                "new_stock": variant.stock_quantity
            })
            
        except Exception as e:
            errors.append({
                "variant_id": update.variant_id,
                "error": str(e)
            })
    
    db.commit()
    
    return {
        "message": f"Successfully updated {len(updated_items)} items",
        "updated_items": updated_items,
        "errors": errors,
        "total_processed": len(bulk_update.updates),
        "successful": len(updated_items),
        "failed": len(errors)
    }


@router.get("/low-stock-count")
async def get_low_stock_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_seller_user)
):
    """Get count of low stock items"""
    
    low_stock_threshold = 10
    low_stock_count = 0
    
    # Get all approved products for this seller
    products = db.query(Product).filter(
        Product.seller_id == current_user.seller.id,
        Product.status != ProductStatus.HIDDEN
    ).all()
    
    for product in products:
        if product.variants and len(product.variants) > 0:
            # Count low stock variants
            for variant in product.variants:
                if variant.is_active and variant.stock_quantity <= low_stock_threshold:
                    low_stock_count += 1
        else:
            # Check base product stock
            if product.stock_quantity <= low_stock_threshold:
                low_stock_count += 1
    
    return {
        "low_stock_count": low_stock_count,
        "threshold": low_stock_threshold
    }

