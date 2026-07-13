import cloudinary
import cloudinary.uploader
from app.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)


def upload_image(file, folder: str = "evenzoo") -> str:
    """
    Uploads a file to Cloudinary and returns the secure URL.
    """
    result = cloudinary.uploader.upload(
        file,
        folder=folder,
        resource_type="image"
    )
    return result["secure_url"]

def delete_image(url: str):
    public_id = url.split("/upload/")[1]
    public_id = public_id.split("/", 1)[1]    
    public_id = public_id.rsplit(".", 1)[0]
    result = cloudinary.uploader.destroy(public_id)
    return result