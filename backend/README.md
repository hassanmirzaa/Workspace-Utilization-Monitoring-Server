# Chair Activity Detection API

Production-ready MVP for real-time chair activity detection using YOLOv8 and MediaPipe. This FastAPI backend processes camera frames from a Flutter mobile app and determines chair status (RED/ORANGE/GREEN) based on person detection and hand-on-table analysis.

## 🎯 Features

- **Real-time Object Detection**: YOLOv8 detects chairs, persons, and tables
- **Hand Detection**: MediaPipe Hands detects hand keypoints
- **Multi-Chair Support**: Handles multiple chairs per frame
- **Three Status System**:
  - 🔴 **RED**: Chair detected, no person sitting
  - 🟠 **ORANGE**: Person sitting, hands NOT on table
  - 🟢 **GREEN**: Person sitting, hands ON table
- **GPU Acceleration**: Optional CUDA support for faster inference
- **Privacy-First**: No face recognition, no identity tracking, no video storage

## 📋 Requirements

- Python 3.8+
- CUDA-capable GPU (optional, for faster inference)
- 4GB+ RAM (8GB+ recommended)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. GPU Setup (Optional)

If you have a CUDA-capable GPU, install PyTorch with CUDA support:

```bash
# For CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

The system will automatically use GPU if available. To force GPU usage, set:
```bash
export USE_GPU=true
```

### 3. Run the Server

```bash
# From backend directory
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 4. Test the API

```bash
# Health check
curl http://localhost:8000/health

# Test inference (replace with your image path)
curl -X POST "http://localhost:8000/infer/frame" \
  -F "file=@test_image.jpg"
```

## 📡 API Endpoints

### 1. Health Check
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2. Frame Inference
```
POST /infer/frame
```

**Request:**
- `file`: JPEG image file (multipart/form-data)
- `camera_id`: Optional camera identifier (form field)

**Response:**
```json
{
  "chairs": [
    {
      "chair_id": "chair_1",
      "status": "GREEN",
      "confidence": 0.87,
      "bbox": [100.5, 200.3, 300.2, 400.1]
    },
    {
      "chair_id": "chair_2",
      "status": "RED",
      "confidence": 0.92,
      "bbox": [500.0, 300.0, 700.0, 500.0]
    }
  ],
  "processing_time_ms": 125.5
}
```

### 3. Annotated Frame
```
POST /infer/frame/annotated
```

**Request:**
- `file`: JPEG image file (multipart/form-data)
- `camera_id`: Optional camera identifier (form field)

**Response:**
- JPEG image with colored bounding boxes:
  - 🔴 Red boxes: Empty chairs
  - 🟠 Orange boxes: Person sitting, hands not on table
  - 🟢 Green boxes: Person sitting, hands on table

## 📱 Flutter Integration

### Example Flutter Request

```dart
import 'dart:io';
import 'package:http/http.dart' as http;

Future<Map<String, dynamic>> detectChairActivity(File imageFile) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('http://your-server:8000/infer/frame'),
  );
  
  request.files.add(
    await http.MultipartFile.fromPath('file', imageFile.path),
  );
  request.fields['camera_id'] = 'camera_1';
  
  var response = await request.send();
  var responseBody = await response.stream.bytesToString();
  
  return jsonDecode(responseBody);
}
```

### Example Flutter Request (Annotated Image)

```dart
Future<Uint8List> getAnnotatedFrame(File imageFile) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('http://your-server:8000/infer/frame/annotated'),
  );
  
  request.files.add(
    await http.MultipartFile.fromPath('file', imageFile.path),
  );
  
  var response = await request.send();
  return await response.stream.toBytes();
}
```

## ⚙️ Configuration

Configuration is managed through environment variables or `app/config.py`. Key settings:

### Detection Thresholds

```python
YOLO_CONFIDENCE_THRESHOLD = 0.25      # YOLO detection confidence
PERSON_CHAIR_OVERLAP_THRESHOLD = 0.3  # IoU threshold for person-chair association
PERSON_CHAIR_CENTROID_DISTANCE_THRESHOLD = 100.0  # Pixel distance threshold
HAND_TABLE_INTERSECTION_THRESHOLD = 0.5  # Fraction of hand keypoints in table
```

### Performance Settings

```python
MAX_FPS = 10  # Maximum frames per second
FRAME_SKIP_THRESHOLD = 0.1  # Skip frame if processing > 100ms
```

### MediaPipe Settings

```python
MEDIAPIPE_HANDS_MODEL_COMPLEXITY = 1  # 0, 1, or 2 (higher = more accurate, slower)
MEDIAPIPE_MAX_NUM_HANDS = 2
MEDIAPIPE_MIN_DETECTION_CONFIDENCE = 0.5
```

### Environment Variables

```bash
# Force GPU usage
export USE_GPU=true

# Custom model path
export YOLO_MODEL_PATH=/path/to/custom/model.pt

# Adjust thresholds
export PERSON_CHAIR_OVERLAP_THRESHOLD=0.4
export HAND_TABLE_INTERSECTION_THRESHOLD=0.6

# API settings
export API_HOST=0.0.0.0
export API_PORT=8000
```

## 🎛️ Threshold Tuning Guide

### Person-Chair Association

If persons are not being associated with chairs:
- **Increase** `PERSON_CHAIR_OVERLAP_THRESHOLD` (e.g., 0.4-0.5)
- **Increase** `PERSON_CHAIR_CENTROID_DISTANCE_THRESHOLD` (e.g., 150-200)

If too many false associations:
- **Decrease** `PERSON_CHAIR_OVERLAP_THRESHOLD` (e.g., 0.2-0.25)
- **Decrease** `PERSON_CHAIR_CENTROID_DISTANCE_THRESHOLD` (e.g., 50-80)

### Hand-on-Table Detection

If hands are not detected on table:
- **Decrease** `HAND_TABLE_INTERSECTION_THRESHOLD` (e.g., 0.3-0.4)
- **Increase** `MEDIAPIPE_HANDS_MODEL_COMPLEXITY` (1 or 2)
- **Decrease** `MEDIAPIPE_MIN_DETECTION_CONFIDENCE` (e.g., 0.3-0.4)

If false positives (hands detected when not on table):
- **Increase** `HAND_TABLE_INTERSECTION_THRESHOLD` (e.g., 0.6-0.7)
- **Increase** `MEDIAPIPE_MIN_DETECTION_CONFIDENCE` (e.g., 0.6-0.7)

### YOLO Detection

If objects are not detected:
- **Decrease** `YOLO_CONFIDENCE_THRESHOLD` (e.g., 0.15-0.2)

If too many false detections:
- **Increase** `YOLO_CONFIDENCE_THRESHOLD` (e.g., 0.3-0.4)

## 🏗️ Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Configuration settings
│   ├── schemas.py              # Pydantic models
│   │
│   ├── routes/
│   │   ├── infer.py            # Frame inference endpoints
│   │   ├── health.py           # Health check endpoint
│   │
│   ├── services/
│   │   ├── detector.py         # YOLOv8 object detection
│   │   ├── pose.py             # MediaPipe hand detection
│   │   ├── chair_mapper.py     # Chair-person association
│   │   ├── status_engine.py    # RED/ORANGE/GREEN logic
│   │
│   └── utils/
│       ├── draw.py             # Visualization utilities
│       └── image.py            # Image encoding/decoding
│
├── requirements.txt
└── README.md
```

## 🔍 Core Logic Flow

1. **Detect Chairs**: YOLOv8 detects all chairs in the frame
2. **Detect Persons**: YOLOv8 detects all persons in the frame
3. **Detect Tables**: YOLOv8 detects tables in the frame
4. **Detect Hands**: MediaPipe detects hand keypoints
5. **Associate Persons to Chairs**: Spatial matching based on overlap/centroid distance
6. **Check Hands-on-Table**: Verify if hand keypoints intersect table bounding box
7. **Assign Status**:
   - No person → RED
   - Person + hands on table → GREEN
   - Person + hands not on table → ORANGE

## 🚨 Error Handling

The API includes comprehensive error handling:
- Invalid image format → 400 Bad Request
- Processing errors → 500 Internal Server Error
- Automatic frame resizing for large images
- Graceful degradation if models fail to load

## 🔒 Privacy & Security

- ✅ No face detection or recognition
- ✅ No identity tracking
- ✅ No video storage (frames processed in-memory only)
- ✅ No persistent data storage
- ✅ CORS configurable for production

## 📊 Performance

### Expected Performance (CPU)
- Processing time: 200-500ms per frame
- Throughput: 2-5 FPS

### Expected Performance (GPU)
- Processing time: 50-150ms per frame
- Throughput: 6-20 FPS

### Optimization Tips
1. Use GPU if available
2. Reduce image resolution in Flutter before sending
3. Adjust `MAX_FPS` to match your needs
4. Use lower `MEDIAPIPE_HANDS_MODEL_COMPLEXITY` for faster processing
5. Consider frame skipping for high-frequency streams

## 🐛 Troubleshooting

### Protobuf/TensorFlow Conflict (Common Issue)

If you see this error:
```
ImportError: cannot import name 'runtime_version' from 'google.protobuf'
```

**Quick Fix:**
```bash
pip uninstall tensorflow
```

This project doesn't use TensorFlow, so uninstalling it resolves the conflict. See `TROUBLESHOOTING.md` for more details.

### Model Download Issues
YOLOv8 will automatically download the model on first run. If download fails:
- Check internet connection
- Manually download from: https://github.com/ultralytics/assets/releases
- Place in project directory or set `YOLO_MODEL_PATH`

### GPU Not Detected
- Verify CUDA installation: `nvidia-smi`
- Install PyTorch with CUDA support (see GPU Setup)
- Check `torch.cuda.is_available()` in Python

### MediaPipe Installation Issues
- Ensure Python 3.8-3.11 (MediaPipe may not support 3.12+)
- If you have TensorFlow installed, uninstall it first: `pip uninstall tensorflow`
- Try: `pip install --upgrade mediapipe`

### Memory Issues
- Reduce `MAX_IMAGE_SIZE` in config
- Process fewer frames per second
- Use smaller YOLO model (yolov8n.pt is smallest)

## 📝 License

This project is provided as-is for MVP purposes.

## 🤝 Contributing

This is an MVP implementation. For production use, consider:
- Adding request rate limiting
- Implementing authentication
- Adding logging and monitoring
- Optimizing for specific hardware
- Adding unit tests
- Implementing model caching strategies
