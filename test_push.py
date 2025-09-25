#!/usr/bin/env python3
"""
Test script to push detection results to the API
"""

import json
import requests
from datetime import datetime
import os

# API Configuration
API_BASE_URL = "http://localhost:8000"  # Change this to your deployed URL
BEARER_TOKEN = "your_bearer_token_for_authentication"  # Update with your actual token

def load_detection_results():
    """Load the detection results from JSON file"""
    try:
        with open('detection_results3.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ detection_results3.json file not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return None

def analyze_detection_results(detection_data):
    """Analyze the detection results and extract occupancy information"""
    if not detection_data:
        return None
    
    # Count occupied and unoccupied seats
    occupied_count = sum(1 for item in detection_data if item['class_name'] == 'occupied')
    unoccupied_count = sum(1 for item in detection_data if item['class_name'] == 'unoccupied')
    total_seats = occupied_count + unoccupied_count
    
    # Calculate occupancy percentage
    occupancy_percentage = (occupied_count / total_seats * 100) if total_seats > 0 else 0
    
    # Extract image info (assuming all detections are from the same image)
    image_path = detection_data[0]['image'] if detection_data else "unknown"
    image_filename = os.path.basename(image_path)
    
    return {
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "image_source": image_filename,
        "total_detections": len(detection_data),
        "occupied_seats": occupied_count,
        "unoccupied_seats": unoccupied_count,
        "total_seats": total_seats,
        "occupancy_percentage": round(occupancy_percentage, 2),
        "detection_confidence_avg": round(sum(item['confidence'] for item in detection_data) / len(detection_data), 4),
        "raw_detections": detection_data
    }

def push_to_api(data, endpoint="push"):
    """Push data to the API endpoint"""
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"{API_BASE_URL}/api/v1/{endpoint}"
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully pushed to {endpoint}")
            print(f"📊 Response: {result.get('message', 'No message')}")
            return result
        else:
            print(f"❌ Failed to push to {endpoint}")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None

def main():
    print("🚌 Bus Seat Detection Results Push Test")
    print("=" * 50)
    
    # Load detection results
    print("📁 Loading detection results...")
    detection_data = load_detection_results()
    if not detection_data:
        return
    
    print(f"✅ Loaded {len(detection_data)} detection results")
    
    # Analyze the results
    print("🔍 Analyzing detection results...")
    analysis = analyze_detection_results(detection_data)
    
    print(f"📊 Analysis Summary:")
    print(f"   - Total seats detected: {analysis['total_seats']}")
    print(f"   - Occupied seats: {analysis['occupied_seats']}")
    print(f"   - Unoccupied seats: {analysis['unoccupied_seats']}")
    print(f"   - Occupancy percentage: {analysis['occupancy_percentage']}%")
    print(f"   - Average confidence: {analysis['detection_confidence_avg']}")
    
    # Test 1: Push to generic endpoint
    print("\n🚀 Test 1: Pushing to generic /api/v1/push endpoint...")
    generic_payload = {
        "data": analysis,
        "metadata": {
            "source": "computer_vision_detection",
            "model_type": "seat_occupancy_detector",
            "processing_timestamp": datetime.utcnow().isoformat()
        }
    }
    
    result1 = push_to_api(generic_payload, "push")
    
    # Test 2: Push to bus occupancy endpoint (structured format)
    print("\n🚀 Test 2: Pushing to /api/v1/bus-occupancy endpoint...")
    bus_payload = {
        "bus_id": "BUS_CV_001",
        "route_id": "ROUTE_DETECTION",
        "occupancy_count": analysis['occupied_seats'],
        "max_capacity": analysis['total_seats'],
        "location": {
            "source": "camera_detection",
            "image_file": analysis['image_source']
        }
    }
    
    result2 = push_to_api(bus_payload, "bus-occupancy")
    
    # Summary
    print("\n📋 Test Summary:")
    print(f"Generic push: {'✅ Success' if result1 else '❌ Failed'}")
    print(f"Bus occupancy push: {'✅ Success' if result2 else '❌ Failed'}")
    
    if result1 or result2:
        print("\n🎉 Data successfully pushed to API!")
        print("💡 Check your Supabase database to see the stored data")
    else:
        print("\n❌ All tests failed. Please check your API configuration.")

if __name__ == "__main__":
    main()
