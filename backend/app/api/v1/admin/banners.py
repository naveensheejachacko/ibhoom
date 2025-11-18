from fastapi import APIRouter, Depends, HTTPException, status as http_status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....core.config import settings
from ....models.user import User
from ....models.banner import Banner, BannerPosition, BannerStatus
from ....models.category import Category
from ....models.product import Product
from ....schemas.banner import BannerCreate, BannerUpdate, BannerResponse, BannerListResponse
from ....schemas.pagination import PaginatedResponse
from ....utils.cloudinary_service import upload_image

router = APIRouter()


@router.post("/", response_model=BannerResponse, status_code=http_status.HTTP_201_CREATED)
async def create_banner(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    position: BannerPosition = Form(BannerPosition.HOME_TOP),
    status: BannerStatus = Form(BannerStatus.DRAFT),
    sort_order: int = Form(0),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    category_id: Optional[str] = Form(None),
    product_id: Optional[str] = Form(None),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new banner with image upload (Admin only)"""
    try:
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Upload image to Cloudinary
        image_url = None
        if settings.CLOUDINARY_URL:
            try:
                result = upload_image(image, folder="banners")
                image_url = result["image_url"]
            except Exception as e:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to upload image: {str(e)}"
                )
        else:
            # If Cloudinary not configured, read as base64
            file_content = await image.read()
            import base64
            base64_string = base64.b64encode(file_content).decode('utf-8')
            image_url = f"data:{image.content_type};base64,{base64_string}"
        
        if not image_url:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Failed to process image"
            )
        
        # Validate category_id and product_id if provided
        if category_id and product_id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify both category_id and product_id. Choose one or neither."
            )
        
        if category_id:
            category = db.query(Category).filter(Category.id == category_id).first()
            if not category:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"Category with id {category_id} not found"
                )
        
        if product_id:
            product = db.query(Product).filter(Product.id == product_id).first()
            if not product:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail=f"Product with id {product_id} not found"
                )
        
        # Parse dates if provided
        parsed_start_date = None
        parsed_end_date = None
        if start_date:
            try:
                parsed_start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                parsed_start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            try:
                parsed_end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                parsed_end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Create banner
        db_banner = Banner(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            image_url=image_url,
            link_url=link_url,
            position=position,
            status=status,
            sort_order=sort_order,
            start_date=parsed_start_date,
            end_date=parsed_end_date,
            category_id=category_id,
            product_id=product_id
        )
        
        db.add(db_banner)
        db.commit()
        db.refresh(db_banner)
        
        return db_banner
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create banner: {str(e)}"
        )


@router.get("/", response_model=PaginatedResponse[BannerListResponse])
async def get_all_banners(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=1000, description="Items per page"),
    position: Optional[BannerPosition] = Query(None),
    status: Optional[BannerStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all banners with filtering (Admin only)"""
    # Calculate skip from page
    skip = (page - 1) * limit
    
    # Build query
    query = db.query(Banner)
    
    if position:
        query = query.filter(Banner.position == position)
    if status:
        query = query.filter(Banner.status == status)
    
    # Get total count
    total = query.count()
    
    # Get banners
    banners = query.order_by(Banner.sort_order.asc(), Banner.created_at.desc()).offset(skip).limit(limit).all()
    
    # Calculate pagination metadata
    current_page = page
    pages = (total + limit - 1) // limit if total > 0 else 1
    
    return PaginatedResponse(
        items=banners,
        total=total,
        page=current_page,
        size=limit,
        pages=pages
    )


@router.get("/{banner_id}", response_model=BannerResponse)
async def get_banner(
    banner_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get banner by ID (Admin only)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Banner not found")
    return banner


@router.put("/{banner_id}", response_model=BannerResponse)
async def update_banner(
    banner_id: str,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    link_url: Optional[str] = Form(None),
    position: Optional[BannerPosition] = Form(None),
    status: Optional[BannerStatus] = Form(None),
    sort_order: Optional[int] = Form(None),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    category_id: Optional[str] = Form(None),
    product_id: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update banner with optional image upload (Admin only)"""
    try:
        banner = db.query(Banner).filter(Banner.id == banner_id).first()
        if not banner:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Banner not found")
        
        # Handle image upload if provided
        if image:
            # Validate image file
            if not image.content_type or not image.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="File must be an image"
                )
            
            # Upload image to Cloudinary
            if settings.CLOUDINARY_URL:
                try:
                    result = upload_image(image, folder="banners")
                    banner.image_url = result["image_url"]
                except Exception as e:
                    raise HTTPException(
                        status_code=http_status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to upload image: {str(e)}"
                    )
            else:
                # If Cloudinary not configured, read as base64
                file_content = await image.read()
                import base64
                base64_string = base64.b64encode(file_content).decode('utf-8')
                banner.image_url = f"data:{image.content_type};base64,{base64_string}"
        
        # Validate category_id and product_id if provided
        # Check if both are being set (even if one is None, we need to check the combination)
        final_category_id = category_id if category_id is not None else banner.category_id
        final_product_id = product_id if product_id is not None else banner.product_id
        
        if final_category_id and final_product_id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot specify both category_id and product_id. Choose one or neither."
            )
        
        if category_id is not None:
            if category_id:  # If not empty string
                category = db.query(Category).filter(Category.id == category_id).first()
                if not category:
                    raise HTTPException(
                        status_code=http_status.HTTP_404_NOT_FOUND,
                        detail=f"Category with id {category_id} not found"
                    )
                banner.category_id = category_id
            else:  # Empty string means clear the mapping
                banner.category_id = None
        
        if product_id is not None:
            if product_id:  # If not empty string
                product = db.query(Product).filter(Product.id == product_id).first()
                if not product:
                    raise HTTPException(
                        status_code=http_status.HTTP_404_NOT_FOUND,
                        detail=f"Product with id {product_id} not found"
                    )
                banner.product_id = product_id
            else:  # Empty string means clear the mapping
                banner.product_id = None
        
        # Update other fields
        if title is not None:
            banner.title = title
        if description is not None:
            banner.description = description
        if link_url is not None:
            banner.link_url = link_url
        if position is not None:
            banner.position = position
        if status is not None:
            banner.status = status
        if sort_order is not None:
            banner.sort_order = sort_order
        if start_date is not None:
            try:
                banner.start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                banner.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date is not None:
            try:
                banner.end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                banner.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        banner.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(banner)
        
        return banner
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update banner: {str(e)}"
        )


@router.delete("/{banner_id}")
async def delete_banner(
    banner_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete banner (Admin only)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Banner not found")
    
    db.delete(banner)
    db.commit()
    
    return {"message": "Banner deleted successfully"}


@router.post("/{banner_id}/track-click")
async def track_banner_click(
    banner_id: str,
    db: Session = Depends(get_db)
):
    """Track banner click (Public endpoint)"""
    banner = db.query(Banner).filter(Banner.id == banner_id).first()
    if not banner:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Banner not found")
    
    banner.click_count += 1
    db.commit()
    
    return {"message": "Click tracked successfully"}

