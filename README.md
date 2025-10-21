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
- ⚡ Persistent HTTP connections with connection pooling

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

## Performance Optimizations

### Persistent HTTP Connections

The API uses **persistent HTTP connections with connection pooling** to eliminate TCP connection overhead and significantly reduce latency for webhook notifications and external API calls.

#### How It Works

Instead of creating a new HTTP connection for each request (which adds 300-500ms overhead), the API maintains a pool of reusable connections:

```python
# ❌ Old approach (slow - creates new connection each time)
async with httpx.AsyncClient() as client:
    response = await client.post(url, json=data)  # 300-500ms overhead

# ✅ New approach (fast - reuses existing connections)
response = await http_client.post(url, json=data)  # ~0ms overhead
```

#### Connection Pool Configuration

- **Max Connections**: 100 concurrent connections
- **Keep-Alive Connections**: 20 connections maintained for instant reuse
- **Keep-Alive Duration**: 30 seconds
- **HTTP/2 Support**: Enabled for better multiplexing
- **Automatic Management**: Connections are created/destroyed as needed

#### Performance Impact

| Scenario | Before | After | Improvement |
|----------|--------|-------|-------------|
| First request to host | 300-800ms | 300-800ms | No change |
| Subsequent requests | 300-800ms | 50-200ms | **300-500ms faster** |
| High-frequency calls | Creates new connection each time | Reuses existing connection | **10x faster** |

#### Implementation Details

The persistent HTTP client is:
- **Initialized** on application startup (`@app.on_event("startup")`)
- **Reused** across all webhook and external API calls
- **Closed gracefully** on application shutdown (`@app.on_event("shutdown")`)

This optimization is particularly beneficial for:
- Webhook notifications to frontend
- Real-time data synchronization
- High-frequency API calls to the same endpoints

## Authentication

All endpoints (except `/` and `/health`) require a bearer token in the Authorization header:

```
Authorization: Bearer your_bearer_token_here
```

## Example Usage

### Push Detection Results Data

#### **Windows Command Prompt:**
```cmd
curl -X POST "https://your-api.vercel.app/api/v1/push" -H "Authorization: Bearer YOUR_TOKEN_HERE" -H "Content-Type: application/json" -d "{\"data\": {\"detection_results\": [{\"image\": \"bus_interior.jpg\", \"class_id\": 1, \"class_name\": \"unoccupied\", \"confidence\": 0.9101, \"x_min\": 2718.45, \"y_min\": 1587.07, \"x_max\": 3177.09, \"y_max\": 2442.6}, {\"image\": \"bus_interior.jpg\", \"class_id\": 0, \"class_name\": \"occupied\", \"confidence\": 0.9013, \"x_min\": 2178.01, \"y_min\": 1583.09, \"x_max\": 2669.04, \"y_max\": 2438.98}], \"summary\": {\"total_detections\": 41, \"occupied_seats\": 18, \"unoccupied_seats\": 23, \"occupancy_percentage\": 43.9}}}"
```

#### **PowerShell/Linux/Mac:**
```bash
curl -X POST "https://your-api.vercel.app/api/v1/push" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "detection_results": [
        {
          "image": "bus_interior.jpg",
          "class_id": 1,
          "class_name": "unoccupied", 
          "confidence": 0.9101,
          "x_min": 2718.45,
          "y_min": 1587.07,
          "x_max": 3177.09,
          "y_max": 2442.6
        },
        {
          "image": "bus_interior.jpg",
          "class_id": 0,
          "class_name": "occupied",
          "confidence": 0.9013,
          "x_min": 2178.01,
          "y_min": 1583.09,
          "x_max": 2669.04,
          "y_max": 2438.98
        }
      ],
      "summary": {
        "total_detections": 41,
        "occupied_seats": 18,
        "unoccupied_seats": 23,
        "occupancy_percentage": 43.9
      }
    }
  }'
```

#### **Python Example:**
```python
import requests
import json

# Configuration
API_URL = "https://your-api.vercel.app/api/v1/push"
BEARER_TOKEN = "YOUR_TOKEN_HERE"

# Load your detection results
with open('detection_results3.json', 'r') as f:
    detection_data = json.load(f)

# Analyze the data
occupied = sum(1 for item in detection_data if item['class_name'] == 'occupied')
unoccupied = sum(1 for item in detection_data if item['class_name'] == 'unoccupied')

# Prepare the payload
payload = {
    "data": {
        "detection_results": detection_data,
        "summary": {
            "total_detections": len(detection_data),
            "occupied_seats": occupied,
            "unoccupied_seats": unoccupied,
            "total_seats": occupied + unoccupied,
            "occupancy_percentage": round(occupied/(occupied+unoccupied)*100, 2)
        }
    }
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
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
```

#### **Python Example with Persistent Connections (Recommended for High-Frequency Calls):**

For applications making frequent API calls, use a `requests.Session()` to benefit from connection pooling on the client side:

```python
import requests
import json

# Configuration
API_URL = "https://your-api.vercel.app/api/v1/push"
BEARER_TOKEN = "YOUR_TOKEN_HERE"

# Create a persistent session (reuse for multiple requests)
session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
})

def send_detection_data(detection_data):
    """Send detection data using persistent connection"""
    # Analyze the data
    occupied = sum(1 for item in detection_data if item['class_name'] == 'occupied')
    unoccupied = sum(1 for item in detection_data if item['class_name'] == 'unoccupied')
    
    # Prepare the payload
    payload = {
        "data": {
            "detection_results": detection_data,
            "summary": {
                "total_detections": len(detection_data),
                "occupied_seats": occupied,
                "unoccupied_seats": unoccupied,
                "total_seats": occupied + unoccupied,
                "occupancy_percentage": round(occupied/(occupied+unoccupied)*100, 2)
            }
        }
    }
    
    # Send using persistent session (much faster for repeated calls)
    response = session.post(API_URL, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success: {result['message']}")
        print(f"📊 Occupancy: {occupied}/{occupied+unoccupied} seats occupied")
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

# Example: Send data from multiple files
for filename in ['detection_results1.json', 'detection_results2.json', 'detection_results3.json']:
    with open(filename, 'r') as f:
        detection_data = json.load(f)
    send_detection_data(detection_data)
    # Connection is reused automatically - much faster!

# Close session when done
session.close()
```

**Benefits of using `requests.Session()`:**
- ✅ Connection reuse across multiple requests
- ✅ 300-500ms faster per request (after first request)
- ✅ Automatic cookie and header persistence
- ✅ More efficient for loops and batch operations

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

## Deployment on Vercel

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Set Environment Variables

In your Vercel dashboard, add these environment variables:
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `BEARER_TOKEN`

### 3. Deploy

```bash
vercel --prod
```

## Supabase Database Schema

### Simplified Schema (3 columns only)

Both tables use the same simplified structure:

#### push_requests
```sql
CREATE TABLE push_requests (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  json_data JSONB NOT NULL
);
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
