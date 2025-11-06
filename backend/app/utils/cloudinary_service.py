"""
Cloudinary service for image upload and management
"""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, List, Dict
from fastapi import UploadFile, HTTPException, status
import io

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def configure_cloudinary(cloudinary_url: str):
    """Configure Cloudinary with the provided URL"""
    try:
        # Strip quotes if present (from .env file)
        cloudinary_url = cloudinary_url.strip().strip('"').strip("'")
        
        if not cloudinary_url:
            raise ValueError("CLOUDINARY_URL is empty")
        
        # Parse the URL: cloudinary://api_key:api_secret@cloud_name
        if not cloudinary_url.startswith("cloudinary://"):
            raise ValueError(f"Invalid CLOUDINARY_URL format. Must start with 'cloudinary://'. Got: {cloudinary_url[:30]}...")
        
        # Remove the cloudinary:// prefix
        url_part = cloudinary_url.replace("cloudinary://", "")
        
        # Split by @ to separate credentials from cloud_name
        if "@" not in url_part:
            raise ValueError(f"Invalid CLOUDINARY_URL format. Missing '@' separator. Got: {cloudinary_url[:30]}...")
        
        credentials, cloud_name = url_part.rsplit("@", 1)
        
        # Split credentials by : to get api_key and api_secret
        if ":" not in credentials:
            raise ValueError(f"Invalid CLOUDINARY_URL format. Missing ':' in credentials. Got: {cloudinary_url[:30]}...")
        
        api_key, api_secret = credentials.split(":", 1)
        
        # Validate all parts are present
        if not cloud_name:
            raise ValueError(f"cloud_name is missing from CLOUDINARY_URL. URL: {cloudinary_url[:30]}...")
        if not api_key:
            raise ValueError(f"api_key is missing from CLOUDINARY_URL. URL: {cloudinary_url[:30]}...")
        if not api_secret:
            raise ValueError(f"api_secret is missing from CLOUDINARY_URL. URL: {cloudinary_url[:30]}...")
        
        # Configure Cloudinary with individual parameters
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True
        )
        
        # Verify configuration
        config = cloudinary.config()
        if not config.cloud_name:
            raise ValueError(f"Failed to configure Cloudinary. cloud_name is missing after configuration.")
        print(f"   Cloudinary configured - Cloud: {config.cloud_name}, API Key: {config.api_key[:4]}...")
    except Exception as e:
        raise ValueError(f"Failed to configure Cloudinary: {str(e)}")


def upload_image(
    file: UploadFile,
    folder: str = "products",
    public_id: Optional[str] = None,
    transformation: Optional[Dict] = None
) -> Dict[str, str]:
    """
    Upload an image to Cloudinary
    
    Args:
        file: FastAPI UploadFile object
        folder: Cloudinary folder to store the image
        public_id: Optional custom public_id for the image
        transformation: Optional image transformations
        
    Returns:
        Dictionary containing image_url, public_id, secure_url
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Read file content
        file_content = file.file.read()
        
        # Validate file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 10MB"
            )
        
        # Optimize image if PIL is available
        if PIL_AVAILABLE:
            try:
                # Open image with PIL to validate
                image = Image.open(io.BytesIO(file_content))
                # Convert to RGB if needed (for PNG with transparency)
                if image.mode in ('RGBA', 'LA', 'P'):
                    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    rgb_image.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
                    image = rgb_image
                
                # Save optimized image to bytes
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=85, optimize=True)
                file_content = output.getvalue()
            except Exception as e:
                # If image processing fails, use original file
                pass
        
        # Upload options
        upload_options = {
            "folder": folder,
            "resource_type": "image",
            "use_filename": True,
            "unique_filename": True,
            "overwrite": False,
        }
        
        # Add public_id if provided
        if public_id:
            upload_options["public_id"] = public_id
        
        # Add transformations if provided
        if transformation:
            upload_options.update(transformation)
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_content,
            **upload_options
        )
        
        return {
            "image_url": result.get("secure_url") or result.get("url"),
            "public_id": result.get("public_id"),
            "width": result.get("width"),
            "height": result.get("height"),
            "format": result.get("format"),
            "bytes": result.get("bytes")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


def upload_image_from_bytes(
    image_bytes: bytes,
    folder: str = "products",
    public_id: Optional[str] = None,
    filename: Optional[str] = None
) -> Dict[str, str]:
    """
    Upload an image from bytes (for base64 or other formats)
    
    Args:
        image_bytes: Image data as bytes
        folder: Cloudinary folder to store the image
        public_id: Optional custom public_id for the image
        filename: Optional filename
        
    Returns:
        Dictionary containing image_url, public_id, secure_url
    """
    try:
        # Validate file size
        max_size = 10 * 1024 * 1024  # 10MB
        if len(image_bytes) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must be less than 10MB"
            )
        
        upload_options = {
            "folder": folder,
            "resource_type": "image",
            "use_filename": True,
            "unique_filename": True,
            "overwrite": False,
        }
        
        if public_id:
            upload_options["public_id"] = public_id
        
        result = cloudinary.uploader.upload(
            image_bytes,
            **upload_options
        )
        
        return {
            "image_url": result.get("secure_url") or result.get("url"),
            "public_id": result.get("public_id"),
            "width": result.get("width"),
            "height": result.get("height"),
            "format": result.get("format"),
            "bytes": result.get("bytes")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload image: {str(e)}"
        )


def upload_base64_image(
    base64_string: str,
    folder: str = "products",
    public_id: Optional[str] = None
) -> Dict[str, str]:
    """
    Upload an image from base64 string
    
    Args:
        base64_string: Base64 encoded image string (with or without data URL prefix)
        folder: Cloudinary folder to store the image
        public_id: Optional custom public_id for the image
        
    Returns:
        Dictionary containing image_url, public_id, secure_url
    """
    try:
        # Check if Cloudinary is configured
        config = cloudinary.config()
        if not config.cloud_name:
            raise ValueError("Cloudinary is not configured. Please set CLOUDINARY_URL environment variable.")
        
        # Remove data URL prefix if present
        if base64_string.startswith('data:image'):
            base64_string = base64_string.split(',')[1]
            if not base64_string:
                raise ValueError("Invalid base64 data: empty after removing data URL prefix")
        
        # Validate base64 string
        if not base64_string:
            raise ValueError("Invalid base64 image data: empty string")
        
        if len(base64_string) < 100:
            raise ValueError(f"Invalid base64 image data: too short ({len(base64_string)} chars, minimum 100)")
        
        # Decode base64 string to bytes
        import base64
        try:
            image_bytes = base64.b64decode(base64_string)
        except Exception as decode_error:
            raise ValueError(f"Invalid base64 encoding: {str(decode_error)}")
        
        # Validate decoded bytes
        if not image_bytes or len(image_bytes) < 100:
            raise ValueError(f"Invalid base64 image data: decoded bytes too short ({len(image_bytes) if image_bytes else 0} bytes, minimum 100)")
        
        # Upload to Cloudinary using bytes
        upload_options = {
            "folder": folder,
            "resource_type": "image",
            "use_filename": True,
            "unique_filename": True,
            "overwrite": False,
        }
        
        if public_id:
            upload_options["public_id"] = public_id
        
        result = cloudinary.uploader.upload(
            image_bytes,
            **upload_options
        )
        
        if not result:
            raise ValueError("Cloudinary upload returned empty result")
        
        image_url = result.get("secure_url") or result.get("url")
        if not image_url:
            raise ValueError("Cloudinary upload did not return a URL")
        
        return {
            "image_url": image_url,
            "public_id": result.get("public_id"),
            "width": result.get("width"),
            "height": result.get("height"),
            "format": result.get("format"),
            "bytes": result.get("bytes")
        }
        
    except ValueError as e:
        # Re-raise ValueError as-is (these are our validation errors)
        raise
    except HTTPException as e:
        # Re-raise HTTPException but convert to ValueError for service layer
        error_msg = e.detail if hasattr(e, 'detail') else str(e)
        print(f"❌ Cloudinary HTTP error: {error_msg}")
        raise ValueError(f"Failed to upload image to Cloudinary: {error_msg}")
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Cloudinary upload error details:\n{error_details}")
        error_msg = str(e) if str(e) else f"Unknown error: {type(e).__name__}"
        raise ValueError(f"Failed to upload image to Cloudinary: {error_msg}")


def delete_image(public_id: str) -> bool:
    """
    Delete an image from Cloudinary
    
    Args:
        public_id: Cloudinary public_id of the image
        
    Returns:
        True if successful
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        # Log error but don't fail
        print(f"Error deleting image from Cloudinary: {str(e)}")
        return False


def extract_public_id_from_url(url: str) -> Optional[str]:
    """
    Extract Cloudinary public_id from a Cloudinary URL
    
    Args:
        url: Cloudinary image URL
        
    Returns:
        public_id or None if not a Cloudinary URL
    """
    try:
        # Cloudinary URLs format: https://res.cloudinary.com/{cloud_name}/image/upload/{version}/{public_id}.{format}
        if "cloudinary.com" in url:
            parts = url.split("/")
            # Find the index of "upload" or "v" (version)
            try:
                upload_index = parts.index("upload")
                # Skip version if present (v1234567890)
                public_id_parts = parts[upload_index + 1:]
                if public_id_parts[0].startswith("v"):
                    public_id_parts = public_id_parts[1:]
                
                # Join remaining parts and remove file extension
                public_id = "/".join(public_id_parts)
                # Remove file extension
                if "." in public_id:
                    public_id = public_id.rsplit(".", 1)[0]
                
                return public_id
            except ValueError:
                return None
        return None
    except Exception:
        return None


def get_image_url(public_id: str, transformation: Optional[Dict] = None) -> str:
    """
    Generate Cloudinary URL from public_id with optional transformations
    
    Args:
        public_id: Cloudinary public_id
        transformation: Optional transformation parameters
        
    Returns:
        Cloudinary image URL
    """
    try:
        if transformation:
            return cloudinary.CloudinaryImage(public_id).build_url(**transformation)
        else:
            return cloudinary.CloudinaryImage(public_id).build_url()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate image URL: {str(e)}"
        )

