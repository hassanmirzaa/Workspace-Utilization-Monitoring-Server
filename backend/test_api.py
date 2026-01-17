#!/usr/bin/env python3
"""
Test script for Chair Activity Detection API.
Run this to test all endpoints on localhost.
"""
import requests
import json
import os
import sys
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health check endpoint."""
    print("\n🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_root():
    """Test root endpoint."""
    print("\n🔍 Testing Root Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_frame_inference(image_path):
    """Test frame inference endpoint."""
    print("\n🔍 Testing Frame Inference (JSON)...")
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            data = {'camera_id': 'test_camera_1'}
            response = requests.post(f"{BASE_URL}/infer/frame", files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Processing Time: {result.get('processing_time_ms', 0):.2f}ms")
            print(f"Chairs Detected: {len(result.get('chairs', []))}")
            for chair in result.get('chairs', []):
                status_emoji = {
                    'RED': '🔴',
                    'ORANGE': '🟠',
                    'GREEN': '🟢'
                }.get(chair['status'], '⚪')
                print(f"  {status_emoji} {chair['chair_id']}: {chair['status']} (confidence: {chair['confidence']:.2f})")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_frame_annotated(image_path):
    """Test annotated frame endpoint."""
    print("\n🔍 Testing Frame Inference (Annotated Image)...")
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return False
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/infer/frame/annotated", files=files)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            # Save annotated image
            output_path = "test_output_annotated.jpg"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Success! Annotated image saved to: {output_path}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_video_inference(video_path):
    """Test video inference endpoint."""
    print("\n🔍 Testing Video Inference (JSON)...")
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return False
    
    try:
        with open(video_path, 'rb') as f:
            files = {'file': (os.path.basename(video_path), f, 'video/mp4')}
            data = {'camera_id': 'test_camera_1', 'process_fps': '2.0'}
            response = requests.post(f"{BASE_URL}/infer/video", files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"Total Frames: {result.get('total_frames', 0)}")
            print(f"Processing Time: {result.get('total_processing_time_ms', 0):.2f}ms")
            print(f"Results: {len(result.get('results', []))} frames processed")
            
            # Show first few results
            for i, frame_result in enumerate(result.get('results', [])[:3]):
                print(f"\n  Frame {i+1} (t={frame_result['timestamp']:.2f}s):")
                for chair in frame_result.get('chairs', []):
                    status_emoji = {
                        'RED': '🔴',
                        'ORANGE': '🟠',
                        'GREEN': '🟢'
                    }.get(chair['status'], '⚪')
                    print(f"    {status_emoji} {chair['chair_id']}: {chair['status']}")
            
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_video_annotated(video_path):
    """Test annotated video endpoint."""
    print("\n🔍 Testing Video Inference (Annotated Video)...")
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        return False
    
    try:
        with open(video_path, 'rb') as f:
            files = {'file': (os.path.basename(video_path), f, 'video/mp4')}
            data = {'process_fps': '2.0'}
            response = requests.post(f"{BASE_URL}/infer/video/annotated", files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            # Save annotated video
            output_path = "test_output_annotated.mp4"
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Success! Annotated video saved to: {output_path}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Chair Activity Detection API Test Suite")
    print("=" * 60)
    
    # Test health and root
    health_ok = test_health()
    root_ok = test_root()
    
    if not health_ok:
        print("\n❌ Server is not running or not accessible!")
        print(f"Make sure the server is running at {BASE_URL}")
        print("Start it with: python -m app.main")
        sys.exit(1)
    
    # Test with image if provided
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        test_frame_inference(image_path)
        test_frame_annotated(image_path)
    
    # Test with video if provided
    if len(sys.argv) > 2:
        video_path = sys.argv[2]
        test_video_inference(video_path)
        test_video_annotated(video_path)
    
    print("\n" + "=" * 60)
    print("✅ Test suite completed!")
    print("=" * 60)
    print("\n📝 Usage:")
    print("  python test_api.py [image_path] [video_path]")
    print("\n📝 Example:")
    print("  python test_api.py test_image.jpg test_video.mp4")

if __name__ == "__main__":
    main()
