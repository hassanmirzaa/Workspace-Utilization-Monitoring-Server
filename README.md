# 🪑 Workspace Utilization Monitoring Server

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-8.0.196-red.svg)](https://ultralytics.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.7-orange.svg)](https://mediapipe.dev/)

Production-ready MVP for real-time chair activity detection using YOLOv8 and MediaPipe. This FastAPI backend processes camera frames from mobile apps and determines chair status (RED/ORANGE/GREEN) based on person detection and hand-on-table analysis.

## 🎯 Features

- **🔴 RED**: Chair detected, no person sitting
- **🟠 ORANGE**: Person sitting, hands NOT on table
- **🟢 GREEN**: Person sitting, hands ON table (productive state)

### Core Capabilities

- ✅ **Real-time Object Detection**: YOLOv8 detects chairs, persons, and tables
- ✅ **Hand Detection**: MediaPipe Hands detects hand keypoints
- ✅ **Multi-Chair Support**: Handles multiple chairs per frame
- ✅ **Video Processing**: Supports MP4, M4V, AVI, MOV formats
- ✅ **Laptop/Desk Work Detection**: Improved detection for laptop work scenarios
- ✅ **GPU Acceleration**: Automatic CUDA detection (CPU fallback)
- ✅ **Privacy-First**: No face recognition, no identity tracking, no video storage

## 📋 Requirements

- Python 3.8+
- CUDA-capable GPU (optional, for faster inference)
- 4GB+ RAM (8GB+ recommended)

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/hassanmirzaa/Workspace-Utilization-Monitoring-Server.git
cd Workspace-Utilization-Monitoring-Server
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note:** If you have TensorFlow installed, you may need to uninstall it:
```bash
pip uninstall tensorflow
```

### 3. Run the Server

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`

### 4. Access Swagger UI

Open your browser: **http://localhost:8000/docs**

## 📡 API Endpoints

### Health Check
```
GET /health
```

### Process Image (JSON)
```
POST /infer/frame
Content-Type: multipart/form-data
- file: Image file (JPEG, PNG)
- camera_id: Optional camera identifier
```

### Process Image (Annotated)
```
POST /infer/frame/annotated
Content-Type: multipart/form-data
- file: Image file (JPEG, PNG)
- camera_id: Optional camera identifier
```

### Process Video (JSON)
```
POST /infer/video
Content-Type: multipart/form-data
- file: Video file (MP4, M4V, AVI, MOV)
- camera_id: Optional camera identifier
- process_fps: FPS to process at (default: Auto - 20% of video FPS)
```

### Process Video (Annotated)
```
POST /infer/video/annotated
Content-Type: multipart/form-data
- file: Video file (MP4, M4V, AVI, MOV)
- camera_id: Optional camera identifier
- process_fps: FPS to process at (default: Auto - 20% of video FPS)
```

## 📊 Response Format

```json
{
  "chairs": [
    {
      "chair_id": "chair_1",
      "status": "GREEN",
      "confidence": 0.87,
      "bbox": [100.5, 200.3, 300.2, 400.1]
    }
  ],
  "processing_time_ms": 125.5
}
```

## 🏗️ Project Structure

```
Workspace-Utilization-Monitoring-Server/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point
│   │   ├── config.py               # Configuration settings
│   │   ├── schemas.py              # Pydantic models
│   │   ├── routes/
│   │   │   ├── infer.py            # Frame inference endpoints
│   │   │   └── health.py           # Health check
│   │   ├── services/
│   │   │   ├── detector.py         # YOLOv8 object detection
│   │   │   ├── pose.py             # MediaPipe hand detection
│   │   │   ├── chair_mapper.py     # Chair-person association
│   │   │   └── status_engine.py    # RED/ORANGE/GREEN logic
│   │   └── utils/
│   │       ├── draw.py             # Visualization utilities
│   │       ├── image.py             # Image encoding/decoding
│   │       └── video.py             # Video processing
│   ├── requirements.txt
│   └── README.md                   # Detailed backend documentation
├── README.md                        # This file
├── FEATURES.md                      # Complete feature list
├── FLUTTER_INTEGRATION.md           # Mobile app integration guide
└── QUICK_START.md                   # Quick reference guide
```

## 🧪 Testing

### Using Swagger UI

1. Start server: `python -m app.main`
2. Open: http://localhost:8000/docs
3. Click "Try it out" on any endpoint
4. Upload your image/video file
5. Execute and view results

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Test with image
curl -X POST "http://localhost:8000/infer/frame" \
  -F "file=@test_image.jpg"

# Test with video
curl -X POST "http://localhost:8000/infer/video/annotated" \
  -F "file=@test_video.mp4" \
  -F "process_fps=15" \
  -o output_annotated.mp4
```

### Using Test Script

```bash
cd backend
python test_api.py [image_path] [video_path]
```

## 📱 Mobile App Integration

See [FLUTTER_INTEGRATION.md](./FLUTTER_INTEGRATION.md) for complete Flutter integration guide with code examples.

## ⚙️ Configuration

All settings can be configured via environment variables or `backend/app/config.py`:

```bash
# Detection thresholds
export YOLO_CONFIDENCE_THRESHOLD=0.25
export PERSON_CHAIR_OVERLAP_THRESHOLD=0.3
export HAND_TABLE_INTERSECTION_THRESHOLD=0.3

# Performance
export MAX_FPS=10
export USE_GPU=true  # Force GPU usage

# API
export API_HOST=0.0.0.0
export API_PORT=8000
```

## 🎨 Color Logic

- **🔴 RED**: Chair detected, **NO person sitting**
- **🟠 ORANGE**: Person sitting, **hands NOT on table**
- **🟢 GREEN**: Person sitting, **hands ON table** (working/productive)

## 🔧 Troubleshooting

### PyTorch 2.6 Compatibility
If you see `weights_only` errors, the code includes automatic fixes. See [PYTORCH_2.6_FIX.md](./backend/PYTORCH_2.6_FIX.md)

### TensorFlow/Protobuf Conflicts
If MediaPipe import fails, uninstall TensorFlow:
```bash
pip uninstall tensorflow
```
See [TROUBLESHOOTING.md](./backend/TROUBLESHOOTING.md) for details.

### M4V File Support
M4V files are fully supported. See [M4_FILE_TESTING.md](./backend/M4_FILE_TESTING.md)

## 📚 Documentation

- [Backend README](./backend/README.md) - Detailed backend documentation
- [Features List](./FEATURES.md) - Complete feature list
- [Flutter Integration](./FLUTTER_INTEGRATION.md) - Mobile app integration
- [Quick Start](./QUICK_START.md) - Quick reference
- [API Testing Guide](./backend/API_TESTING_GUIDE.md) - API testing guide
- [Swagger Guide](./backend/SWAGGER_GUIDE.md) - Swagger UI guide

## 🚀 Performance

### Expected Performance (CPU)
- Processing time: 200-500ms per frame
- Throughput: 2-5 FPS

### Expected Performance (GPU)
- Processing time: 50-150ms per frame
- Throughput: 6-20 FPS

## 🔒 Privacy & Security

- ✅ No face detection or recognition
- ✅ No identity tracking
- ✅ No video storage (frames processed in-memory only)
- ✅ No persistent data storage
- ✅ CORS configurable for production

## 📝 License

This project is provided as-is for MVP purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Built with ❤️ using FastAPI, YOLOv8, and MediaPipe**
