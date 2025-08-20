from typing import Dict, Tuple
from urllib.parse import urlparse
from fastapi import UploadFile, HTTPException, status
from starlette.concurrency import run_in_threadpool
import cloudinary.uploader

from src.conf.config import settings


def _allowed_mime_set() -> set[str]:
    raw = settings.ALLOWED_MIME or ""
    return {s.strip().lower() for s in raw.split(",") if s.strip()}


def _get_cloudinary_creds() -> Tuple[str, str, str]:
    if settings.CLD_NAME and settings.CLD_API_KEY and settings.CLD_API_SECRET:
        return (
            str(settings.CLD_NAME),
            str(settings.CLD_API_KEY),
            str(settings.CLD_API_SECRET),
        )
    if settings.CLOUDINARY_URL:
        u = urlparse(settings.CLOUDINARY_URL)
        cloud_name = u.hostname
        api_key = u.username
        api_secret = u.password
        if cloud_name and api_key and api_secret:
            return cloud_name, api_key, api_secret
    raise RuntimeError(
        "Cloudinary creds missing. Set CLOUDINARY_URL "
        "or CLD_NAME/CLD_API_KEY/CLD_API_SECRET"
    )


async def cloudinary_upload(file: UploadFile, *, folder: str = "messenger") -> Dict:
    allowed = _allowed_mime_set()
    mime = (file.content_type or "application/octet-stream").strip().lower()
    if allowed and mime not in allowed:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported media type: {mime}",
        )

    content = await file.read()
    size = len(content)
    if size > int(settings.MAX_UPLOAD_MB) * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large (> {settings.MAX_UPLOAD_MB}MB)",
        )

    cloud_name, api_key, api_secret = _get_cloudinary_creds()

    def _upload():
        return cloudinary.uploader.upload(
            content,
            resource_type="auto",
            folder=folder,
            use_filename=True,
            unique_filename=True,
            overwrite=False,
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
        )

    try:
        res = await run_in_threadpool(_upload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Cloudinary upload failed: {e}",
        )

    return {
        "file_path": res["secure_url"],
        "file_name": file.filename or res["public_id"],
        "mime": mime,
        "size_bytes": res.get("bytes"),
        "storage": "cloudinary",
        "provider_id": res["public_id"],
        "resource_type": res.get("resource_type"),
    }
