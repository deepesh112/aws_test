"""Lambda handler for deleting an image."""
from typing import Any, Dict

from src.utils import response, dynamodb, s3


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle DELETE /images/{id} request."""
    path_params = event.get("pathParameters") or {}
    image_id = path_params.get("id")

    if not image_id:
        return response.bad_request("Missing image ID")

    try:
        metadata = dynamodb.get_image_metadata(image_id)

        if not metadata:
            return response.not_found(f"Image not found: {image_id}")

        s3_key = metadata.get("s3_key")

        s3.delete_image(s3_key)

        dynamodb.delete_image_metadata(image_id)

        return response.success({
            "message": "Image deleted successfully",
            "image_id": image_id
        })

    except Exception as e:
        return response.server_error(str(e))
