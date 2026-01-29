"""Lambda handler for getting/downloading an image."""
import base64
from typing import Any, Dict

from src.utils import response, dynamodb, s3


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle GET /images/{id} request."""
    path_params = event.get("pathParameters") or {}
    image_id = path_params.get("id")

    if not image_id:
        return response.bad_request("Missing image ID")

    query_params = event.get("queryStringParameters") or {}
    download = query_params.get("download", "").lower() == "true"

    try:
        metadata = dynamodb.get_image_metadata(image_id)

        if not metadata:
            return response.not_found(f"Image not found: {image_id}")

        s3_key = metadata.get("s3_key")

        if download:
            image_data = s3.get_image(s3_key)
            if not image_data:
                return response.not_found("Image file not found in storage")

            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": metadata.get("content_type", "application/octet-stream"),
                    "Content-Disposition": f'attachment; filename="{metadata.get("filename")}"',
                    "Access-Control-Allow-Origin": "*"
                },
                "body": base64.b64encode(image_data).decode("utf-8"),
                "isBase64Encoded": True
            }

        download_url = s3.get_presigned_url(s3_key)

        return response.success({
            "image": metadata,
            "download_url": download_url
        })

    except Exception as e:
        return response.server_error(str(e))
