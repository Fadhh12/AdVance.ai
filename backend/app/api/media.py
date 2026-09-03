"""FR-02: upload photo/video to the media library. Validates type + size server-side
(SRS §2.2) — never trust the frontend's own checks.
"""
import tempfile
import uuid
from typing import IO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.models.base import get_db
from app.models.media_asset import MediaAsset
from app.models.user import User
from app.schemas.media import MediaAssetOut
from app.services.storage import delete_object, generate_presigned_url, upload_object

router = APIRouter()

# SRS §2.2: foto <=20MB (jpg/png/webp), video mentah <=500MB (mp4/mov)
PHOTO_CONTENT_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
VIDEO_CONTENT_TYPES = {"video/mp4": ".mp4", "video/quicktime": ".mov"}
PHOTO_MAX_BYTES = 20 * 1024 * 1024
VIDEO_MAX_BYTES = 500 * 1024 * 1024
_CHUNK_SIZE = 1024 * 1024


def _read_with_limit(fileobj, max_bytes: int) -> tuple[IO[bytes], int]:
    """Spools to disk past 10MB so a 500MB video upload doesn't sit in RAM, and aborts
    as soon as the declared limit is crossed instead of buffering the whole thing first.
    """
    spooled = tempfile.SpooledTemporaryFile(max_size=10 * 1024 * 1024)
    total = 0
    while chunk := fileobj.read(_CHUNK_SIZE):
        total += len(chunk)
        if total > max_bytes:
            spooled.close()
            raise HTTPException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                f"Ukuran file melebihi batas {max_bytes // (1024 * 1024)}MB.",
            )
        spooled.write(chunk)
    spooled.seek(0)
    return spooled, total


def _to_out(asset: MediaAsset) -> MediaAssetOut:
    return MediaAssetOut(
        id=asset.id,
        type=asset.type,
        original_filename=asset.original_filename,
        content_type=asset.content_type,
        size_bytes=asset.size_bytes,
        uploaded_at=asset.uploaded_at,
        url=generate_presigned_url(asset.file_url),
    )


@router.post("/upload", response_model=MediaAssetOut, status_code=status.HTTP_201_CREATED)
def upload_media(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type in PHOTO_CONTENT_TYPES:
        asset_type, max_bytes, ext = (
            "photo",
            PHOTO_MAX_BYTES,
            PHOTO_CONTENT_TYPES[file.content_type],
        )
    elif file.content_type in VIDEO_CONTENT_TYPES:
        asset_type, max_bytes, ext = (
            "video_raw",
            VIDEO_MAX_BYTES,
            VIDEO_CONTENT_TYPES[file.content_type],
        )
    else:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Format tidak didukung. Foto: jpg/png/webp. Video: mp4/mov.",
        )

    spooled, size = _read_with_limit(file.file, max_bytes)
    if size == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File kosong.")

    key = f"media/{current_user.id}/{uuid.uuid4()}{ext}"
    upload_object(key, spooled, file.content_type)

    asset = MediaAsset(
        user_id=current_user.id,
        type=asset_type,
        file_url=key,
        original_filename=file.filename or "upload",
        content_type=file.content_type,
        size_bytes=size,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return _to_out(asset)


@router.get("", response_model=list[MediaAssetOut])
def list_media(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assets = db.execute(
        select(MediaAsset)
        .where(MediaAsset.user_id == current_user.id)
        .order_by(MediaAsset.uploaded_at.desc())
    ).scalars()
    return [_to_out(asset) for asset in assets]


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_media(
    media_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    asset = db.execute(
        select(MediaAsset).where(
            MediaAsset.id == media_id, MediaAsset.user_id == current_user.id
        )
    ).scalar_one_or_none()
    if asset is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Media tidak ditemukan.")

    delete_object(asset.file_url)
    db.delete(asset)
    db.commit()
