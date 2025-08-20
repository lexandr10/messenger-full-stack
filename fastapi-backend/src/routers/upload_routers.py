from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.core.depend_service import get_current_user
from src.storage.cloudinary_adapter import cloudinary_upload

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=List[Dict])
async def upload_file(
    files: List[UploadFile] = File(..., description="1..N files"),
    folder: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    target_folder = folder or f"users/{current_user.id}"

    out: List[Dict] = []
    for f in files:
        meta = await cloudinary_upload(f, folder=target_folder)
        out.append(
            {
                "file_path": meta["file_path"],
                "file_name": meta["file_name"],
                "mime": meta["mime"],
                "size_bytes": meta["size_bytes"],
                "storage": meta["storage"],
                "provider_id": meta["provider_id"],
            }
        )

    return out
