#!/usr/bin/env python3
"""
Production API test with your detection results
"""

import json
import requests
from datetime import datetime

# Your deployed Vercel API URL
API_BASE_URL = "https://api-push-2oek.vercel.app"
BEARER_TOKEN = "7a450d69-8ef6-4249-87cf-70cf7ce0d621"

def test_api_calls():
    """Test all API endpoints"""
    
    # Headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("🚀 Testing Production API")
    print("=" * 50)
    
    # Test 1: Health check (no auth required)
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 2: Load and send detection results
    print("\n2️⃣ Testing Detection Results Push...")
    
    # Load your detection data
    try:
        with open('detection_results3.json', 'r') as f:
            detection_data = json.load(f)
        
        # Analyze the data
        occupied = sum(1 for item in detection_data if item['class_name'] == 'occupied')
        unoccupied = sum(1 for item in detection_data if item['class_name'] == 'unoccupied')
        
        # Prepare payload
        payload = {
            "data": {
                "detection_results": detection_data,
                "analysis": {
                    "total_detections": len(detection_data),
                    "occupied_seats": occupied,
                    "unoccupied_seats": unoccupied,
                    "total_seats": occupied + unoccupied,
                    "occupancy_percentage": round(occupied/(occupied+unoccupied)*100, 2),
                    "processed_at": datetime.utcnow().isoformat()
                }
            },
            "metadata": {
                "source": "computer_vision_model",
                "image_source": "bus_interior_camera",
                "model_confidence_avg": round(sum(item['confidence'] for item in detection_data) / len(detection_data), 4)
            }
        }
        
        # Send to generic push endpoint
        response = requests.post(
            f"{API_BASE_URL}/api/v1/push",
            json=payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['message']}")
            print(f"📊 Data processed: {occupied}/{occupied+unoccupied} seats occupied")
        else:
            print(f"❌ Failed: {response.text}")
            
    except FileNotFoundError:
        print("❌ detection_results3.json not found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Bus occupancy endpoint
    print("\n3️⃣ Testing Bus Occupancy Endpoint...")
    
    bus_payload = {
        "bus_id": "BUS_CV_001",
        "route_id": "DETECTION_ROUTE",
        "occupancy_count": occupied if 'occupied' in locals() else 18,
        "max_capacity": occupied + unoccupied if 'occupied' in locals() else 41,
        "location": {
            "type": "camera_detection",
            "camera_id": "interior_cam_01",
            "detection_timestamp": datetime.utcnow().isoformat()
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/bus-occupancy",
            json=bus_payload,
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result['message']}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Get bus occupancy data
    print("\n4️⃣ Testing Get Bus Occupancy...")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1/bus-occupancy/BUS_CV_001",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved data: {result['message']}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("⚠️  Make sure to update API_BASE_URL and BEARER_TOKEN!")
    test_api_calls()
