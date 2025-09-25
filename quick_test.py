#!/usr/bin/env python3
"""
Quick test to push the detection results JSON directly
"""

import json
import requests
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/v1/push"  # Change to your deployed URL
BEARER_TOKEN = "your_bearer_token_for_authentication"  # Update with your token

def main():
    # Load the detection results
    with open('detection_results3.json', 'r') as f:
        detection_data = json.load(f)
    
    # Count seats for quick analysis
    occupied = sum(1 for item in detection_data if item['class_name'] == 'occupied')
    unoccupied = sum(1 for item in detection_data if item['class_name'] == 'unoccupied')
    
    print(f"🔍 Detection Summary:")
    print(f"   Occupied seats: {occupied}")
    print(f"   Unoccupied seats: {unoccupied}")
    print(f"   Total detections: {len(detection_data)}")
    print(f"   Occupancy: {occupied/(occupied+unoccupied)*100:.1f}%")
    
    # Prepare payload for API
    payload = {
        "data": {
            "detection_results": detection_data,
            "summary": {
                "occupied_seats": occupied,
                "unoccupied_seats": unoccupied,
                "total_seats": occupied + unoccupied,
                "occupancy_percentage": round(occupied/(occupied+unoccupied)*100, 2)
            },
            "timestamp": datetime.utcnow().isoformat()
        },
        "metadata": {
            "source": "computer_vision",
            "model": "seat_detection",
            "image_analyzed": "1075488_dataset 2025-09-16 23-04-32_image_20250916_164708_f.jpg"
        }
    }
    
    # Push to API
    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }
    
    print(f"\n🚀 Pushing data to {API_URL}...")
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"📋 API Response: {result['message']}")
            print(f"⏰ Timestamp: {result['timestamp']}")
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
