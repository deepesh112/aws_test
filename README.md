# Image Management API

A serverless REST API for image management built with AWS Lambda, API Gateway, S3, and DynamoDB.

## Architecture

- **API Gateway**: RESTful API endpoints
- **Lambda**: Python 3.9 handlers for business logic
- **S3**: Image file storage
- **DynamoDB**: Image metadata storage

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/images` | Upload an image with metadata |
| GET | `/images` | List images with filters |
| GET | `/images/{id}` | Get image metadata and download URL |
| DELETE | `/images/{id}` | Delete an image |

---

## API Documentation

### 1. Upload Image

**POST** `/images`

Upload a new image with metadata.

**Request Body:**
```json
{
  "image_data": "<base64-encoded-image>",
  "filename": "photo.jpg",
  "content_type": "image/jpeg",
  "user_id": "user123",
  "description": "My vacation photo"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| image_data | string | Yes | Base64-encoded image data |
| filename | string | Yes | Original filename |
| content_type | string | Yes | MIME type (e.g., image/jpeg, image/png) |
| user_id | string | Yes | User identifier |
| description | string | No | Image description |

**Response (201 Created):**
```json
{
  "message": "Image uploaded successfully",
  "image": {
    "image_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "photo.jpg",
    "content_type": "image/jpeg",
    "size": 102400,
    "user_id": "user123",
    "upload_date": "2024-01-15T10:30:00.000000",
    "description": "My vacation photo",
    "s3_key": "images/550e8400-e29b-41d4-a716-446655440000/photo.jpg"
  }
}
```

**Example (curl):**
```bash
# Encode image to base64
IMAGE_DATA=$(base64 -i photo.jpg)

curl -X POST https://<api-id>.execute-api.<region>.amazonaws.com/dev/images \
  -H "Content-Type: application/json" \
  -d "{
    \"image_data\": \"$IMAGE_DATA\",
    \"filename\": \"photo.jpg\",
    \"content_type\": \"image/jpeg\",
    \"user_id\": \"user123\",
    \"description\": \"My vacation photo\"
  }"
```

---

### 2. List Images

**GET** `/images`

List images with optional filters.

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | string | Yes | Filter by user ID |
| start_date | string | No | Filter images uploaded after this date (ISO format) |
| end_date | string | No | Filter images uploaded before this date (ISO format) |
| limit | integer | No | Max items to return (1-100, default: 20) |
| next_token | string | No | Pagination token for next page |

**Response (200 OK):**
```json
{
  "images": [
    {
      "image_id": "550e8400-e29b-41d4-a716-446655440000",
      "filename": "photo.jpg",
      "content_type": "image/jpeg",
      "size": 102400,
      "user_id": "user123",
      "upload_date": "2024-01-15T10:30:00.000000",
      "s3_key": "images/550e8400-e29b-41d4-a716-446655440000/photo.jpg"
    }
  ],
  "count": 1,
  "next_token": "eyJ1c2VyX2lkIjogInVzZXIxMjMifQ=="
}
```

**Examples (curl):**
```bash
# List all images for a user
curl "https://<api-id>.execute-api.<region>.amazonaws.com/dev/images?user_id=user123"

# Filter by date range
curl "https://<api-id>.execute-api.<region>.amazonaws.com/dev/images?user_id=user123&start_date=2024-01-01T00:00:00&end_date=2024-01-31T23:59:59"

# With pagination
curl "https://<api-id>.execute-api.<region>.amazonaws.com/dev/images?user_id=user123&limit=10"
```

---

### 3. Get/Download Image

**GET** `/images/{id}`

Get image metadata and download URL.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Image ID |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| download | boolean | If "true", returns image binary directly |

**Response (200 OK) - Metadata mode:**
```json
{
  "image": {
    "image_id": "550e8400-e29b-41d4-a716-446655440000",
    "filename": "photo.jpg",
    "content_type": "image/jpeg",
    "size": 102400,
    "user_id": "user123",
    "upload_date": "2024-01-15T10:30:00.000000",
    "s3_key": "images/550e8400-e29b-41d4-a716-446655440000/photo.jpg"
  },
  "download_url": "https://s3.amazonaws.com/bucket/images/...?X-Amz-Signature=..."
}
```

**Response (200 OK) - Download mode:**
Returns the image binary with appropriate Content-Type header.

**Examples (curl):**
```bash
# Get metadata and presigned URL
curl "https://<api-id>.execute-api.<region>.amazonaws.com/dev/images/550e8400-e29b-41d4-a716-446655440000"

# Download image directly
curl -o downloaded.jpg "https://<api-id>.execute-api.<region>.amazonaws.com/dev/images/550e8400-e29b-41d4-a716-446655440000?download=true"
```

---

### 4. Delete Image

**DELETE** `/images/{id}`

Delete an image and its metadata.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| id | string | Image ID |

**Response (200 OK):**
```json
{
  "message": "Image deleted successfully",
  "image_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Example (curl):**
```bash
curl -X DELETE "https://<api-id>.execute-api.<region>.amazonaws.com/dev/images/550e8400-e29b-41d4-a716-446655440000"
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Missing or invalid parameters |
| 404 | Not Found - Image does not exist |
| 500 | Internal Server Error |

---

## Setup & Deployment

### Prerequisites

- Python 3.9+
- AWS CLI configured with appropriate credentials
- AWS SAM CLI

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

3. **Run tests with coverage:**
   ```bash
   pytest tests/ -v --cov=src --cov-report=html
   ```

### Deployment

1. **Build the application:**
   ```bash
   sam build
   ```

2. **Deploy (first time):**
   ```bash
   sam deploy --guided
   ```

3. **Deploy (subsequent):**
   ```bash
   sam deploy
   ```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| IMAGES_TABLE | DynamoDB table name | images |
| IMAGES_BUCKET | S3 bucket name | image-storage-bucket |

---

## Project Structure

```
aws_test/
├── src/
│   ├── handlers/
│   │   ├── upload_image.py    # POST /images
│   │   ├── list_images.py     # GET /images
│   │   ├── get_image.py       # GET /images/{id}
│   │   └── delete_image.py    # DELETE /images/{id}
│   └── utils/
│       ├── dynamodb.py        # DynamoDB operations
│       ├── s3.py              # S3 operations
│       └── response.py        # API response helpers
├── tests/
│   ├── conftest.py            # Test fixtures
│   ├── test_upload_image.py
│   ├── test_list_images.py
│   ├── test_get_image.py
│   └── test_delete_image.py
├── template.yaml              # SAM template
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## DynamoDB Schema

**Table: images-{stage}**

| Attribute | Type | Key |
|-----------|------|-----|
| image_id | String | Partition Key |
| user_id | String | GSI Partition Key |
| upload_date | String | GSI Sort Key |
| filename | String | - |
| content_type | String | - |
| size | Number | - |
| description | String | - |
| s3_key | String | - |

**Global Secondary Index: user_id-index**
- Partition Key: user_id
- Sort Key: upload_date
- Enables efficient querying by user and date range
