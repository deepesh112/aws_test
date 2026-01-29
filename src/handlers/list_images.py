"""Lambda handler for listing images."""
from typing import Any, Dict

from src.utils import response, dynamodb


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle GET /images request."""
    query_params = event.get("queryStringParameters") or {}

    user_id = query_params.get("user_id")
    if not user_id:
        return response.bad_request("Missing required query parameter: user_id")

    start_date = query_params.get("start_date")
    end_date = query_params.get("end_date")
    next_token = query_params.get("next_token")

    try:
        limit = int(query_params.get("limit", "20"))
        if limit < 1 or limit > 100:
            return response.bad_request("Limit must be between 1 and 100")
    except ValueError:
        return response.bad_request("Invalid limit value")

    try:
        images, new_next_token = dynamodb.list_images(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            next_token=next_token
        )

        result = {
            "images": images,
            "count": len(images)
        }

        if new_next_token:
            result["next_token"] = new_next_token

        return response.success(result)

    except Exception as e:
        return response.server_error(str(e))
