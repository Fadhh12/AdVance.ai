"""S3-compatible object storage wrapper (MinIO locally, swap for R2/S3 in prod via
.env only). SDD §3.6: bucket is private — never return a permanent public URL, always
a short-lived signed one, generated fresh on read and never persisted.
"""
import boto3
from botocore.client import Config as BotoConfig

from app.core.config import get_settings


def get_s3_client():
    settings = get_settings()
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=BotoConfig(
            signature_version="s3v4",
            s3={"addressing_style": "path" if settings.s3_use_path_style else "auto"},
        ),
    )


def upload_object(key: str, fileobj, content_type: str) -> None:
    settings = get_settings()
    get_s3_client().upload_fileobj(
        fileobj, settings.s3_bucket_name, key, ExtraArgs={"ContentType": content_type}
    )


def delete_object(key: str) -> None:
    settings = get_settings()
    get_s3_client().delete_object(Bucket=settings.s3_bucket_name, Key=key)


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    settings = get_settings()
    return get_s3_client().generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket_name, "Key": key},
        ExpiresIn=expires_in,
    )
