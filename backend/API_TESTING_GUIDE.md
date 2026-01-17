# API Testing Guide

## 🚀 Quick Start - Run Server on Localhost

### 1. Start the Server

```bash
cd backend
python -m app.main
```

The server will start at: `http://localhost:8000`

### 2. Test Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 3. Test with Image

```bash
curl -X POST "http://localhost:8000/infer/frame" \
  -F "file=@your_image.jpg" \
  -F "camera_id=test_camera"
```

### 4. Test with Video

```bash
curl -X POST "http://localhost:8000/infer/video" \
  -F "file=@your_video.mp4" \
  -F "camera_id=test_camera" \
  -F "process_fps=2.0"
```

---

## 📡 Available Endpoints

### **1. Health Check**
```
GET /health
```

### **2. Frame Inference (JSON)**
```
POST /infer/frame
Content-Type: multipart/form-data

Parameters:
- file: Image file (JPEG, PNG)
- camera_id: Optional camera identifier

Response:
{
  "chairs": [
    {
      "chair_id": "chair_1",
      "status": "GREEN",  // RED, ORANGE, or GREEN
      "confidence": 0.87,
      "bbox": [x1, y1, x2, y2]
    }
  ],
  "processing_time_ms": 125.5
}
```

### **3. Frame Inference (Annotated Image)**
```
POST /infer/frame/annotated
Content-Type: multipart/form-data

Parameters:
- file: Image file (JPEG, PNG)
- camera_id: Optional camera identifier

Response: JPEG image with colored bounding boxes
```

### **4. Video Inference (JSON)**
```
POST /infer/video
Content-Type: multipart/form-data

Parameters:
- file: Video file (MP4, AVI, MOV)
- camera_id: Optional camera identifier
- process_fps: FPS to process at (default: 2.0)

Response:
{
  "total_frames": 60,
  "fps": 30.0,
  "results": [
    {
      "timestamp": 0.0,
      "chairs": [...]
    },
    {
      "timestamp": 0.5,
      "chairs": [...]
    }
  ],
  "total_processing_time_ms": 5000.0
}
```

### **5. Video Inference (Annotated Video)**
```
POST /infer/video/annotated
Content-Type: multipart/form-data

Parameters:
- file: Video file (MP4, AVI, MOV)
- camera_id: Optional camera identifier
- process_fps: FPS to process at (default: 2.0)

Response: MP4 video file with colored bounding boxes
```

---

## 🎨 Color Logic (Confirmed)

- **🔴 RED**: Chair detected, **NO person sitting**
- **🟢 GREEN**: Person sitting **AND hands ON table**
- **🟠 ORANGE**: Person sitting **BUT hands NOT on table**

---

## 🧪 Automated Testing

### Run Test Script

```bash
cd backend
python test_api.py [image_path] [video_path]
```

Example:
```bash
python test_api.py test_image.jpg test_video.mp4
```

The script will:
1. Test health check
2. Test frame inference (JSON)
3. Test frame inference (annotated image)
4. Test video inference (JSON)
5. Test video inference (annotated video)

---

## 📝 Python Test Examples

### Test Frame Inference

```python
import requests

url = "http://localhost:8000/infer/frame"
with open("test_image.jpg", "rb") as f:
    files = {"file": ("test.jpg", f, "image/jpeg")}
    data = {"camera_id": "test_camera"}
    response = requests.post(url, files=files, data=data)

print(response.json())
```

### Test Video Inference

```python
import requests

url = "http://localhost:8000/infer/video"
with open("test_video.mp4", "rb") as f:
    files = {"file": ("test.mp4", f, "video/mp4")}
    data = {"camera_id": "test_camera", "process_fps": "2.0"}
    response = requests.post(url, files=files, data=data)

result = response.json()
print(f"Processed {result['total_frames']} frames")
for frame_result in result['results']:
    print(f"Frame at {frame_result['timestamp']}s: {len(frame_result['chairs'])} chairs")
```

---

## 🌐 Access from Mobile/Remote

### Find Your Local IP

**macOS/Linux:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```cmd
ipconfig
```

### Update Server Host

The server is configured to listen on `0.0.0.0:8000` by default, which means it's accessible from:
- `http://localhost:8000` (same machine)
- `http://YOUR_IP:8000` (same network)

### Test from Mobile

1. Find your computer's IP (e.g., `192.168.1.100`)
2. Ensure phone is on same WiFi network
3. Use: `http://192.168.1.100:8000/infer/frame`

---

## 🔍 API Documentation

Once server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 🐛 Troubleshooting

### Server Not Starting
- Check if port 8000 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Connection Refused
- Ensure server is running: `python -m app.main`
- Check firewall settings
- Verify you're using correct IP address

### Slow Processing
- Reduce `process_fps` for videos (e.g., 1.0 or 2.0)
- Use lower resolution images/videos
- Consider GPU acceleration if available

---

**All APIs are now live and ready for testing! 🎉**
