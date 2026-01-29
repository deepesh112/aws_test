"""Lambda handler for uploading images."""
import base64
import json
import uuid
from typing import Any, Dict

from src.utils import response, dynamodb, s3


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle POST /images request."""
    try:
        body = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return response.bad_request("Invalid JSON body")

    image_data_b64 = body.get("image_data")
    if not image_data_b64:
        return response.bad_request("Missing required field: image_data")

    filename = body.get("filename")
    if not filename:
        return response.bad_request("Missing required field: filename")

    content_type = body.get("content_type")
    if not content_type:
        return response.bad_request("Missing required field: content_type")

    user_id = body.get("user_id")
    if not user_id:
        return response.bad_request("Missing required field: user_id")

    description = body.get("description")

    try:
        image_data = base64.b64decode(image_data_b64)
    except Exception:
        return response.bad_request("Invalid base64 image data")

    image_id = str(uuid.uuid4())

    try:
        s3_key = s3.upload_image(image_data, image_id, filename, content_type)

        metadata = dynamodb.save_image_metadata(
            image_id=image_id,
            filename=filename,
            content_type=content_type,
            size=len(image_data),
            user_id=user_id,
            s3_key=s3_key,
            description=description
        )

        return response.created({
            "message": "Image uploaded successfully",
            "image": metadata
        })

    except Exception as e:
        return response.server_error(str(e))
