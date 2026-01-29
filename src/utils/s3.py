"""S3 operations for image storage."""
import os
from typing import Optional

import boto3
from botocore.exceptions import ClientError


def get_bucket_name() -> str:
    """Get S3 bucket name from environment."""
    return os.environ.get("IMAGES_BUCKET", "image-storage-bucket")


def get_s3_client():
    """Get S3 client."""
    return boto3.client("s3")


def upload_image(
    image_data: bytes,
    image_id: str,
    filename: str,
    content_type: str
) -> str:
    """Upload image to S3."""
    s3 = get_s3_client()
    bucket = get_bucket_name()

    s3_key = f"images/{image_id}/{filename}"

    s3.put_object(
        Bucket=bucket,
        Key=s3_key,
        Body=image_data,
        ContentType=content_type
    )

    return s3_key


def get_presigned_url(s3_key: str, expiration: int = 3600) -> str:
    """Generate presigned URL for image download."""
    s3 = get_s3_client()
    bucket = get_bucket_name()

    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": s3_key},
        ExpiresIn=expiration
    )

    return url


def get_image(s3_key: str) -> Optional[bytes]:
    """Get image data from S3."""
    s3 = get_s3_client()
    bucket = get_bucket_name()

    try:
        response = s3.get_object(Bucket=bucket, Key=s3_key)
        return response["Body"].read()
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchKey":
            return None
        raise


def delete_image(s3_key: str) -> bool:
    """Delete image from S3."""
    s3 = get_s3_client()
    bucket = get_bucket_name()

    s3.delete_object(Bucket=bucket, Key=s3_key)

    return True
