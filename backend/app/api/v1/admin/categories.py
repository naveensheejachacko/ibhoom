from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from ....core.database import get_db
from ....core.dependencies import get_admin_user
from ....models.user import User
from ....schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithChildren, CategoryTree
from ....services import category_service
from ....utils.cloudinary_service import upload_image
from ....core.config import settings

router = APIRouter()


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    parent_id: Optional[str] = Form(None),
    sort_order: int = Form(0),
    is_active: bool = Form(True),
    icon: Optional[UploadFile] = File(None),
    icon_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new category with optional icon upload (Admin only)"""
    try:
        # Handle icon upload
        final_icon_url = icon_url
        
        if icon:
            # Validate file type
            if not icon.content_type or not icon.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Icon must be an image file"
                )
            
            # Upload to Cloudinary if configured
            if settings.CLOUDINARY_URL:
                try:
                    result = upload_image(icon, folder="categories")
                    final_icon_url = result["image_url"]
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to upload icon: {str(e)}"
                    )
            else:
                # If Cloudinary not configured, read as base64
                file_content = await icon.read()
                import base64
                import io
                base64_string = base64.b64encode(file_content).decode('utf-8')
                final_icon_url = f"data:{icon.content_type};base64,{base64_string}"
        
        # Create category data
        category_data = CategoryCreate(
            name=name,
            description=description,
            icon_url=final_icon_url,
            parent_id=parent_id if parent_id else None,
            sort_order=sort_order,
            is_active=is_active
        )
        
        db_category = category_service.create_category(db, category_data)
        return db_category
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    parent_id: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get categories with optional filtering (Admin only)"""
    categories = category_service.get_categories(
        db, skip=skip, limit=limit, parent_id=parent_id, active_only=active_only
    )
    return categories


@router.get("/tree", response_model=List[CategoryWithChildren])
async def get_category_tree(
    parent_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get hierarchical category tree (Admin only)"""
    categories = category_service.get_category_tree(db, parent_id)
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get category by ID (Admin only)"""
    category = category_service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category


@router.get("/{category_id}/path", response_model=List[CategoryResponse])
async def get_category_path(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get full path from root to category (Admin only)"""
    path = category_service.get_category_path(db, category_id)
    if not path:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return path


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    parent_id: Optional[str] = Form(None),
    sort_order: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    icon: Optional[UploadFile] = File(None),
    icon_url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update category with optional icon upload (Admin only)"""
    try:
        # Handle icon upload
        final_icon_url = icon_url
        
        if icon:
            # Validate file type
            if not icon.content_type or not icon.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Icon must be an image file"
                )
            
            # Upload to Cloudinary if configured
            if settings.CLOUDINARY_URL:
                try:
                    result = upload_image(icon, folder="categories")
                    final_icon_url = result["image_url"]
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to upload icon: {str(e)}"
                    )
            else:
                # If Cloudinary not configured, read as base64
                file_content = await icon.read()
                import base64
                base64_string = base64.b64encode(file_content).decode('utf-8')
                final_icon_url = f"data:{icon.content_type};base64,{base64_string}"
        
        # Create update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if final_icon_url is not None:
            update_data["icon_url"] = final_icon_url
        if parent_id is not None:
            update_data["parent_id"] = parent_id if parent_id else None
        if sort_order is not None:
            update_data["sort_order"] = sort_order
        if is_active is not None:
            update_data["is_active"] = is_active
        
        category_update = CategoryUpdate(**update_data)
        updated_category = category_service.update_category(db, category_id, category_update)
        if not updated_category:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return updated_category
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete category (Admin only)"""
    try:
        deleted = category_service.delete_category(db, category_id)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
        return {"message": "Category deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get category by slug (Admin only)"""
    category = category_service.get_category_by_slug(db, slug)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category 