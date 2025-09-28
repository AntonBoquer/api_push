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

#### **Python Example (Simple):**
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

#### **Python Implementation (Advanced):**
```python
#!/usr/bin/env python3
"""
Advanced Python client for Bus Occupancy API Push System
Supports both detection_results and detections formats with comprehensive error handling
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BusOccupancyAPIClient:
    """Advanced client for Bus Occupancy API with comprehensive features"""
    
    def __init__(self, api_url: str, bearer_token: str, timeout: int = 30):
        """
        Initialize the API client
        
        Args:
            api_url: Base URL of the API
            bearer_token: Bearer token for authentication
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip('/')
        self.bearer_token = bearer_token
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'BusOccupancyClient/1.0'
        })
    
    def health_check(self) -> Dict:
        """Check API health and connectivity"""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=self.timeout)
            response.raise_for_status()
            return {"status": "healthy", "data": response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    def load_detection_data(self, file_path: str) -> Optional[Dict]:
        """Load detection data from JSON file with format detection"""
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            
            # Handle different JSON formats
            if isinstance(data, dict):
                if 'detections' in data:
                    logger.info(f"Loaded data with 'detections' key ({len(data['detections'])} items)")
                    return data
                elif 'detection_results' in data:
                    logger.info(f"Loaded data with 'detection_results' key ({len(data['detection_results'])} items)")
                    return data
                elif isinstance(data.get('data'), list):
                    # Direct array in data field
                    return {'detections': data['data']}
            elif isinstance(data, list):
                # Direct array format
                logger.info(f"Loaded direct array format ({len(data)} items)")
                return {'detections': data}
            
            logger.warning("Unrecognized JSON format")
            return data
            
        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
            return None
    
    def analyze_detections(self, detections: List[Dict]) -> Tuple[int, int, int, float]:
        """Analyze detection data and return statistics"""
        occupied = sum(1 for d in detections if d.get('class_id') == 0 or d.get('class_name') == 'occupied')
        unoccupied = sum(1 for d in detections if d.get('class_id') == 1 or d.get('class_name') == 'unoccupied')
        total = len(detections)
        occupancy_rate = (occupied / total * 100) if total > 0 else 0
        
        return occupied, unoccupied, total, occupancy_rate
    
    def prepare_payload(self, data: Dict, include_summary: bool = True) -> Dict:
        """Prepare API payload from detection data"""
        # Extract detections from various formats
        detections = []
        inference_time = data.get('inference_time_sec', 0.0)
        
        if 'detections' in data:
            detections = data['detections']
            detection_key = 'detections'
        elif 'detection_results' in data:
            detections = data['detection_results']
            detection_key = 'detection_results'
        else:
            logger.error("No detections found in data")
            return {}
        
        # Analyze detections
        occupied, unoccupied, total, occupancy_rate = self.analyze_detections(detections)
        
        # Prepare payload
        payload = {
            "data": {
                detection_key: detections
            }
        }
        
        # Add inference time if available
        if inference_time > 0:
            payload["data"]["inference_time_sec"] = inference_time
        
        # Add summary if requested
        if include_summary:
            payload["data"]["summary"] = {
                "total_detections": total,
                "occupied_seats": occupied,
                "unoccupied_seats": unoccupied,
                "occupancy_percentage": round(occupancy_rate, 1),
                "timestamp": datetime.now().isoformat()
            }
        
        return payload
    
    def push_detection_data(self, payload: Dict, endpoint: str = "/api/v1/push") -> Dict:
        """Push detection data to the API"""
        try:
            url = f"{self.api_url}{endpoint}"
            logger.info(f"Sending request to {url}")
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Success: {result.get('message', 'Request completed')}")
            return {
                "success": True,
                "status_code": response.status_code,
                "data": result
            }
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {response.status_code}: {response.text}"
            logger.error(error_msg)
            return {
                "success": False,
                "status_code": response.status_code,
                "error": error_msg,
                "response_text": response.text
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def push_from_file(self, file_path: str, endpoint: str = "/api/v1/push") -> Dict:
        """Load detection data from file and push to API"""
        # Load data
        data = self.load_detection_data(file_path)
        if not data:
            return {"success": False, "error": "Failed to load detection data"}
        
        # Prepare payload
        payload = self.prepare_payload(data)
        if not payload:
            return {"success": False, "error": "Failed to prepare payload"}
        
        # Push to API
        return self.push_detection_data(payload, endpoint)

# Example usage and testing
def main():
    """Example usage of the BusOccupancyAPIClient"""
    
    # Configuration
    API_URL = "https://your-api.vercel.app"  # Replace with your API URL
    BEARER_TOKEN = "YOUR_TOKEN_HERE"         # Replace with your bearer token
    
    # Initialize client
    client = BusOccupancyAPIClient(API_URL, BEARER_TOKEN)
    
    # Health check
    print("🏥 Checking API health...")
    health = client.health_check()
    if health["status"] == "healthy":
        print("✅ API is healthy")
    else:
        print(f"❌ API health check failed: {health.get('error')}")
        return
    
    # Push detection data from file
    json_file = "detection_results3.json"  # Replace with your file path
    
    print(f"\n📤 Pushing detection data from {json_file}...")
    result = client.push_from_file(json_file)
    
    if result["success"]:
        data = result["data"]
        summary = data.get("data", {}).get("summary", {})
        print(f"✅ Data pushed successfully!")
        print(f"📊 Summary:")
        print(f"   • Total detections: {summary.get('total_detections', 'N/A')}")
        print(f"   • Occupied seats: {summary.get('occupied_seats', 'N/A')}")
        print(f"   • Unoccupied seats: {summary.get('unoccupied_seats', 'N/A')}")
        print(f"   • Occupancy rate: {summary.get('occupancy_percentage', 'N/A')}%")
    else:
        print(f"❌ Failed to push data: {result.get('error')}")
        if 'response_text' in result:
            print(f"📝 Response: {result['response_text']}")

if __name__ == "__main__":
    main()
```

#### **Quick Python Script:**
```python
# quick_push.py - Simple script to push detection data
import requests
import json
import sys

def quick_push(file_path, api_url, token):
    """Quick function to push detection data to API"""
    
    # Load data
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Extract detections (handle both formats)
    detections = data.get('detections') or data.get('detection_results', [])
    
    # Count occupancy
    occupied = sum(1 for d in detections if d.get('class_id') == 0)
    total = len(detections)
    
    # Prepare payload
    payload = {
        "data": {
            "detections": detections,
            "summary": {
                "total_detections": total,
                "occupied_seats": occupied,
                "unoccupied_seats": total - occupied,
                "occupancy_percentage": round(occupied/total*100, 1) if total > 0 else 0
            }
        }
    }
    
    # Send request
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(f"{api_url}/api/v1/push", json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Success! Pushed {total} detections ({occupied} occupied)")
        return True
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        return False

# Usage: python quick_push.py detection_results3.json
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_push.py <json_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    api_url = "https://your-api.vercel.app"  # Replace with your URL
    token = "YOUR_TOKEN_HERE"                # Replace with your token
    
    quick_push(file_path, api_url, token)
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
