import cloudinary
import cloudinary.uploader
from src.conf.config import settings


cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True
)

def upload_avatar(file):
    result = cloudinary.uploader.upload(file)
    return result["secure_url"]