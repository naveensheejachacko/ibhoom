"""
Utility functions for handling return request images
"""
import os
import uuid
import json
from typing import List
from fastapi import UploadFile
from ..core.config import settings


def save_return_image(file_content: bytes, filename: str) -> str:
    """Save return image and return the file path"""
    # Create return_images directory if it doesn't exist
    upload_dir = os.path.join(settings.UPLOAD_DIR, "return_images")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Generate unique filename
    file_extension = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Return relative path for storage in database
    return f"uploads/return_images/{unique_filename}"


async def save_return_images(files: List[UploadFile], max_files: int = 5) -> List[str]:
    """
    Save multiple return images
    
    Args:
        files: List of uploaded files
        max_files: Maximum number of files allowed (default: 5)
    
    Returns:
        List of saved image paths
    """
    if len(files) > max_files:
        raise ValueError(f"Maximum {max_files} images allowed")
    
    saved_paths = []
    
    for file in files:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise ValueError(f"File {file.filename} is not an image")
        
        # Validate file size (5MB limit per image)
        file_content = await file.read()
        if len(file_content) > 5 * 1024 * 1024:  # 5MB
            raise ValueError(f"File {file.filename} exceeds 5MB size limit")
        
        # Save image
        image_path = save_return_image(file_content, file.filename or "image.jpg")
        saved_paths.append(image_path)
    
    return saved_paths


def images_to_json(image_paths: List[str]) -> str:
    """Convert list of image paths to JSON string"""
    return json.dumps(image_paths)


def json_to_images(json_str: str) -> List[str]:
    """Convert JSON string to list of image paths"""
    if not json_str:
        return []
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return []


def delete_return_image(image_path: str) -> bool:
    """Delete a return image file"""
    try:
        # Handle both relative and absolute paths
        if not image_path.startswith('/'):
            # Relative path - prepend with uploads directory
            full_path = os.path.join(settings.UPLOAD_DIR, image_path.replace('uploads/', ''))
        else:
            full_path = image_path
        
        if os.path.exists(full_path):
            os.remove(full_path)
        return True
    except Exception:
        return False


def delete_return_images(image_paths: List[str]) -> None:
    """Delete multiple return image files"""
    for path in image_paths:
        delete_return_image(path)



