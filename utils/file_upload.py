# utils/file_upload.py
import os, uuid
from fastapi import UploadFile
from typing import Tuple
from core.config import get_settings
settings = get_settings()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
BASE_UPLOAD_DIR = "uploads"
# If AWS credentials set in .env, use S3
USE_S3 = bool(getattr(settings, "AWS_S3_BUCKET", None))

if USE_S3:
    import boto3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=getattr(settings, "AWS_REGION", None)
    )

async def save_file(file: UploadFile, folder: str) -> Tuple[str, str]:
    ext = file.filename.split(".")[-1].lower()
    media_type = "video" if ext in ["mp4", "mov", "avi", "mkv"] else "image"
    filename = f"{uuid.uuid4().hex}.{ext}"

    if USE_S3:
        # upload to S3
        bucket = settings.AWS_S3_BUCKET
        s3.upload_fileobj(file.file, bucket, filename, ExtraArgs={"ACL":"public-read"})
        url = f"https://{bucket}.s3.amazonaws.com/{filename}"
        return url, media_type
    else:
        upload_path = os.path.join(BASE_UPLOAD_DIR, folder)
        os.makedirs(upload_path, exist_ok=True)
        path = os.path.join(upload_path, filename)
        with open(path, "wb") as f:
            f.write(await file.read())
        return path.replace("\\", "/")
    