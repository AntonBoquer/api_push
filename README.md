# Bus Occupancy API Push System

A Python FastAPI application for handling push requests with bearer token authentication and Supabase database integration. Designed for deployment on Vercel.

## Features

- 🔐 Bearer token authentication
- 📡 RESTful API endpoints for push requests
- 🚌 Specialized bus occupancy data handling
- 🗄️ Supabase database integration
- 🚀 Ready for Vercel deployment
- 📊 Comprehensive logging and error handling
- 🔍 Health check endpoints
- 📝 Automatic API documentation
- 🔔 Webhook notifications to frontend on new detection data

## Quick Start

### 1. Environment Setup

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# API Security
BEARER_TOKEN=your_bearer_token_for_authentication

# Webhook Configuration (Optional)
FRONTEND_WEBHOOK_URL=https://your-frontend.vercel.app/api/webhook/new-data
WEBHOOK_SECRET=your-webhook-secret-key

# Environment
ENVIRONMENT=development
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Locally

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/health` - Check API health and database connectivity

### General Push Endpoint
- **POST** `/api/v1/push` - Handle generic JSON push requests

### Bus Occupancy Specific
- **POST** `/api/v1/bus-occupancy` - Update bus occupancy data
- **GET** `/api/v1/bus-occupancy/{bus_id}` - Get current bus occupancy

## Authentication

All endpoints (except `/` and `/health`) require a bearer token in the Authorization header:

```
Authorization: Bearer your_bearer_token_here
```

## Example Usage

### Push Detection Results Data

#### **Payload Field Descriptions:**
- `uuid` (optional): Unique identifier for the detection batch
- `detection_results` (required): Array of detection objects
  - `image`: Image file path/name
  - `x_min`, `y_min`, `x_max`, `y_max`: Bounding box coordinates
  - `class_id`: 0 for occupied, 1 for unoccupied
  - `class_name`: "occupied" or "unoccupied"
  - `confidence`: Detection confidence score (0.0 to 1.0)
- `summary` (optional): Summary statistics object
- `metadata` (optional): Additional metadata dictionary
- `processed` (optional): Processing status boolean
- `timestamp` (optional): Custom timestamp
- `received_at` (optional): When the data was received
- `inference_time_sec` (optional): Time taken for inference

#### **Request Payload Structure:**
```json
{
  "uuid": "5b1e5f62-4c90-4d7b-b0c6-37c7287d501a",
  "detection_results": [
    {
      "image": "tiles/image_20250930_172500_left.jpg",
      "x_min": 1351.92,
      "y_min": 1507.96,
      "x_max": 1674.40,
      "y_max": 1725.51,
      "class_id": 1,
      "class_name": "unoccupied",
      "confidence": 0.8774
    }
  ],
  "summary": null,
  "metadata": {},
  "processed": true,
  "timestamp": null,
  "received_at": "2025-09-30T17:25:05.704753+08:00",
  "inference_time_sec": 0.5928
}
```

#### **PowerShell/Linux/Mac:**
```bash
curl -X POST "https://your-api.vercel.app/api/v1/push" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "uuid": "5b1e5f62-4c90-4d7b-b0c6-37c7287d501a",
    "detection_results": [
      {
        "image": "tiles/image_20250930_172500_left.jpg",
        "x_min": 1351.92,
        "y_min": 1507.96,
        "x_max": 1674.40,
        "y_max": 1725.51,
        "class_id": 1,
        "class_name": "unoccupied",
        "confidence": 0.8774
      },
      {
        "image": "tiles/image_20250930_172500_left.jpg",
        "x_min": 1465.35,
        "y_min": 1388.22,
        "x_max": 1727.89,
        "y_max": 1506.17,
        "class_id": 0,
        "class_name": "occupied",
        "confidence": 0.8153
      }
    ],
    "metadata": {},
    "processed": true,
    "received_at": "2025-09-30T17:25:05.704753+08:00",
    "inference_time_sec": 0.5928
  }'
```

#### **Python Example:**
```python
import requests
import json
from datetime import datetime
import uuid

# Configuration
API_URL = "https://your-api.vercel.app/api/v1/push"
BEARER_TOKEN = "YOUR_TOKEN_HERE"

# Load your detection results
with open('detection_results3.json', 'r') as f:
    detection_data = json.load(f)

# Analyze the data
occupied = sum(1 for item in detection_data if item['class_name'] == 'occupied')
unoccupied = sum(1 for item in detection_data if item['class_name'] == 'unoccupied')

# Prepare the payload with new structure
payload = {
    "uuid": str(uuid.uuid4()),
    "detection_results": detection_data,
    "summary": {
        "total_detections": len(detection_data),
        "occupied_seats": occupied,
        "unoccupied_seats": unoccupied,
        "total_seats": occupied + unoccupied,
        "occupancy_percentage": round(occupied/(occupied+unoccupied)*100, 2)
    },
    "metadata": {},
    "processed": True,
    "received_at": datetime.utcnow().isoformat() + "Z",
    "inference_time_sec": 0.5928  # Add your actual inference time
}

# Send the request
headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}

response = requests.post(API_URL, json=payload, headers=headers)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Success: {result['message']}")
    print(f"📊 Occupancy: {occupied}/{occupied+unoccupied} seats occupied")
    print(f"🔑 UUID: {payload['uuid']}")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
```

### Update Bus Occupancy

```bash
curl -X POST "https://your-api.vercel.app/api/v1/bus-occupancy" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "bus_id": "BUS_001",
    "route_id": "ROUTE_A1",
    "occupancy_count": 25,
    "max_capacity": 50,
    "location": {
      "latitude": 40.7128,
      "longitude": -74.0060
    }
  }'
```

## Webhook Notifications

When new detection data is pushed to `/api/v1/push`, the API automatically sends a webhook notification to your configured frontend endpoint.

### Webhook Configuration

Set these environment variables:
- `FRONTEND_WEBHOOK_URL` - Your frontend webhook endpoint URL
- `WEBHOOK_SECRET` - Shared secret for authentication

### Webhook Payload Format

The webhook sends the following JSON payload:

```json
{
  "event": "new_detection_data",
  "record_id": 3004,
  "inference_time_sec": 0.5928,
  "detection_results": [
    {
      "image": "tiles/image_20250930_172500_left.jpg",
      "x_min": 1351.92,
      "y_min": 1507.96,
      "x_max": 1674.40,
      "y_max": 1725.51,
      "class_id": 1,
      "class_name": "unoccupied",
      "confidence": 0.8774
    }
  ],
  "timestamp": "2025-09-30T17:25:05.704753+08:00",
  "secret": "your-webhook-secret"
}
```

### Frontend Webhook Handler Example

```python
from fastapi import FastAPI, HTTPException
import os

app = FastAPI()

@app.post("/api/webhook/new-data")
async def receive_webhook(webhook_data: dict):
    # Verify the webhook secret
    if webhook_data.get("secret") != os.getenv("WEBHOOK_SECRET"):
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    
    # Extract detection data
    record_id = webhook_data["record_id"]
    detection_results = webhook_data["detection_results"]
    inference_time = webhook_data["inference_time_sec"]
    
    # Process the detection results
    # ... your processing logic here ...
    
    return {"status": "received", "record_id": record_id}
```

## Deployment on Vercel

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Set Environment Variables

In your Vercel dashboard, add these environment variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon/service key
- `BEARER_TOKEN` - API authentication token
- `FRONTEND_WEBHOOK_URL` - (Optional) Frontend webhook endpoint
- `WEBHOOK_SECRET` - (Optional) Webhook authentication secret

### 3. Deploy

```bash
vercel --prod
```

## Supabase Database Schema

### Simplified Schema

Both tables use a simplified structure with optional uuid column:

#### push_requests
```sql
CREATE TABLE push_requests (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  uuid TEXT,
  json_data JSONB NOT NULL
);

-- Add index for uuid lookups
CREATE INDEX IF NOT EXISTS idx_push_requests_uuid ON push_requests(uuid);
```

#### bus_occupancy
```sql
CREATE TABLE bus_occupancy (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  json_data JSONB NOT NULL
);
```

**Column Descriptions:**
- `id`: Auto-incrementing primary key
- `created_at`: Automatically set timestamp when record is created
- `uuid`: (push_requests only) Extracted UUID for easy querying
- `json_data`: All the actual data stored as JSON (flexible structure)

## Response Format

All endpoints return responses in this format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Development

### Running with Auto-reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation

When running in development mode, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Security Considerations

1. **Bearer Token**: Use a strong, randomly generated bearer token (this is your only authentication)
2. **HTTPS**: Always use HTTPS in production
3. **CORS**: Configure CORS properly for your domain
4. **Environment Variables**: Never commit sensitive data to version control
5. **Rate Limiting**: Consider implementing rate limiting for production use

## Error Handling

The API includes comprehensive error handling:
- 401: Invalid or missing bearer token
- 404: Resource not found
- 422: Validation errors
- 500: Internal server errors

## Logging

All requests and errors are logged with appropriate levels:
- INFO: Successful operations
- WARNING: Invalid authentication attempts
- ERROR: System errors and exceptions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
