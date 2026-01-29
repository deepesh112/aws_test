"""API Gateway response helpers."""
import json
from decimal import Decimal
from typing import Any, Dict, Optional


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal types from DynamoDB."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            if obj % 1 == 0:
                return int(obj)
            return float(obj)
        return super().default(obj)


def create_response(
    status_code: int,
    body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create an API Gateway response."""
    default_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS"
    }

    if headers:
        default_headers.update(headers)

    response = {
        "statusCode": status_code,
        "headers": default_headers,
    }

    if body is not None:
        response["body"] = json.dumps(body, cls=DecimalEncoder)

    return response


def success(body: Dict[str, Any], status_code: int = 200) -> Dict[str, Any]:
    """Create a success response."""
    return create_response(status_code, body)


def created(body: Dict[str, Any]) -> Dict[str, Any]:
    """Create a 201 Created response."""
    return create_response(201, body)


def bad_request(message: str) -> Dict[str, Any]:
    """Create a 400 Bad Request response."""
    return create_response(400, {"error": message})


def not_found(message: str = "Resource not found") -> Dict[str, Any]:
    """Create a 404 Not Found response."""
    return create_response(404, {"error": message})


def server_error(message: str = "Internal server error") -> Dict[str, Any]:
    """Create a 500 Internal Server Error response."""
    return create_response(500, {"error": message})
