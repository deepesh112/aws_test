"""DynamoDB operations for image metadata."""
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import boto3
from boto3.dynamodb.conditions import Key, Attr


def get_table():
    """Get DynamoDB table resource."""
    dynamodb = boto3.resource("dynamodb")
    table_name = os.environ.get("IMAGES_TABLE", "images")
    return dynamodb.Table(table_name)


def save_image_metadata(
    image_id: str,
    filename: str,
    content_type: str,
    size: int,
    user_id: str,
    s3_key: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """Save image metadata to DynamoDB."""
    table = get_table()

    upload_date = datetime.now(timezone.utc).isoformat()

    item = {
        "image_id": image_id,
        "filename": filename,
        "content_type": content_type,
        "size": size,
        "user_id": user_id,
        "s3_key": s3_key,
        "upload_date": upload_date,
    }

    if description:
        item["description"] = description

    table.put_item(Item=item)

    return item


def get_image_metadata(image_id: str) -> Optional[Dict[str, Any]]:
    """Get image metadata by ID."""
    table = get_table()

    response = table.get_item(Key={"image_id": image_id})

    return response.get("Item")


def list_images(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 20,
    next_token: Optional[str] = None
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """List images with filters."""
    table = get_table()

    key_condition = Key("user_id").eq(user_id)

    if start_date and end_date:
        key_condition = key_condition & Key("upload_date").between(start_date, end_date)
    elif start_date:
        key_condition = key_condition & Key("upload_date").gte(start_date)
    elif end_date:
        key_condition = key_condition & Key("upload_date").lte(end_date)

    query_params = {
        "IndexName": "user_id-index",
        "KeyConditionExpression": key_condition,
        "Limit": limit,
    }

    if next_token:
        import json
        import base64
        query_params["ExclusiveStartKey"] = json.loads(
            base64.b64decode(next_token).decode("utf-8")
        )

    response = table.query(**query_params)

    items = response.get("Items", [])

    new_next_token = None
    if "LastEvaluatedKey" in response:
        import json
        import base64
        new_next_token = base64.b64encode(
            json.dumps(response["LastEvaluatedKey"]).encode("utf-8")
        ).decode("utf-8")

    return items, new_next_token


def delete_image_metadata(image_id: str) -> bool:
    """Delete image metadata from DynamoDB."""
    table = get_table()

    table.delete_item(Key={"image_id": image_id})

    return True
