# Flutter Mobile App Integration Guide

## 🎯 Available Features

### ✅ **1. Real-Time Chair Activity Detection**
- **YOLOv8 Object Detection**: Detects chairs, persons, and tables in real-time
- **MediaPipe Hand Detection**: Detects hand keypoints to determine if hands are on table
- **Multi-Chair Support**: Handles multiple chairs in a single frame
- **Three-State Classification**:
  - 🔴 **RED**: Chair detected, no person sitting
  - 🟠 **ORANGE**: Person sitting, hands NOT on table
  - 🟢 **GREEN**: Person sitting, hands ON table

### ✅ **2. API Endpoints**

#### **Health Check**
- `GET /health` - Check if server is running

#### **Frame Inference (JSON Response)**
- `POST /infer/frame` - Returns JSON with chair statuses and bounding boxes

#### **Annotated Frame (Image Response)**
- `POST /infer/frame/annotated` - Returns JPEG image with colored bounding boxes

### ✅ **3. Response Data**
- Chair ID (unique identifier per chair)
- Status (RED/ORANGE/GREEN)
- Confidence score (0.0 to 1.0)
- Bounding box coordinates [x1, y1, x2, y2]
- Processing time in milliseconds

---

## 📱 Flutter Integration

### **Step 1: Add Dependencies**

Add these to your `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  camera: ^0.10.5+9
  http: ^1.1.0
  image: ^4.1.3
  path_provider: ^2.1.1
```

### **Step 2: Create API Service**

Create `lib/services/chair_detection_service.dart`:

```dart
import 'dart:io';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:image/image.dart' as img;

class ChairDetectionService {
  final String baseUrl;
  
  ChairDetectionService({this.baseUrl = 'http://localhost:8000'});
  
  /// Check if server is healthy
  Future<bool> checkHealth() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: {'Content-Type': 'application/json'},
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
  
  /// Process frame and get chair statuses (JSON response)
  Future<FrameInferenceResponse> detectChairActivity(
    File imageFile, {
    String? cameraId,
  }) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/infer/frame'),
    );
    
    // Add image file
    request.files.add(
      await http.MultipartFile.fromPath('file', imageFile.path),
    );
    
    // Add optional camera_id
    if (cameraId != null) {
      request.fields['camera_id'] = cameraId;
    }
    
    final response = await request.send();
    final responseBody = await response.stream.bytesToString();
    
    if (response.statusCode == 200) {
      final json = jsonDecode(responseBody);
      return FrameInferenceResponse.fromJson(json);
    } else {
      throw Exception('Failed to detect chairs: ${response.statusCode}');
    }
  }
  
  /// Process frame and get annotated image
  Future<List<int>> getAnnotatedFrame(
    File imageFile, {
    String? cameraId,
  }) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/infer/frame/annotated'),
    );
    
    request.files.add(
      await http.MultipartFile.fromPath('file', imageFile.path),
    );
    
    if (cameraId != null) {
      request.fields['camera_id'] = cameraId;
    }
    
    final response = await request.send();
    
    if (response.statusCode == 200) {
      return await response.stream.toBytes();
    } else {
      throw Exception('Failed to get annotated frame: ${response.statusCode}');
    }
  }
}

/// Response model
class FrameInferenceResponse {
  final List<ChairStatus> chairs;
  final double? processingTimeMs;
  
  FrameInferenceResponse({
    required this.chairs,
    this.processingTimeMs,
  });
  
  factory FrameInferenceResponse.fromJson(Map<String, dynamic> json) {
    return FrameInferenceResponse(
      chairs: (json['chairs'] as List)
          .map((c) => ChairStatus.fromJson(c))
          .toList(),
      processingTimeMs: json['processing_time_ms']?.toDouble(),
    );
  }
}

/// Chair status model
class ChairStatus {
  final String chairId;
  final String status; // "RED", "ORANGE", or "GREEN"
  final double confidence;
  final List<double> bbox; // [x1, y1, x2, y2]
  
  ChairStatus({
    required this.chairId,
    required this.status,
    required this.confidence,
    required this.bbox,
  });
  
  factory ChairStatus.fromJson(Map<String, dynamic> json) {
    return ChairStatus(
      chairId: json['chair_id'],
      status: json['status'],
      confidence: (json['confidence'] as num).toDouble(),
      bbox: (json['bbox'] as List).map((e) => (e as num).toDouble()).toList(),
    );
  }
  
  /// Get status color
  int getStatusColor() {
    switch (status) {
      case 'RED':
        return 0xFFFF0000; // Red
      case 'ORANGE':
        return 0xFFFFA500; // Orange
      case 'GREEN':
        return 0xFF00FF00; // Green
      default:
        return 0xFF808080; // Gray
    }
  }
}
```

### **Step 3: Camera Integration**

Create `lib/screens/camera_screen.dart`:

```dart
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:path_provider/path_provider.dart';
import '../services/chair_detection_service.dart';

class CameraScreen extends StatefulWidget {
  @override
  _CameraScreenState createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  CameraController? _controller;
  List<CameraDescription>? _cameras;
  bool _isProcessing = false;
  ChairDetectionService _service = ChairDetectionService(
    baseUrl: 'http://YOUR_SERVER_IP:8000', // Replace with your server IP
  );
  FrameInferenceResponse? _lastResponse;
  
  @override
  void initState() {
    super.initState();
    _initializeCamera();
  }
  
  Future<void> _initializeCamera() async {
    _cameras = await availableCameras();
    if (_cameras != null && _cameras!.isNotEmpty) {
      _controller = CameraController(
        _cameras![0],
        ResolutionPreset.medium, // Use medium for better performance
        enableAudio: false,
      );
      
      await _controller!.initialize();
      setState(() {});
      
      // Start continuous frame processing
      _startFrameProcessing();
    }
  }
  
  void _startFrameProcessing() {
    // Process frames at 5-10 FPS
    Future.delayed(Duration(milliseconds: 200), () {
      if (_controller != null && _controller!.value.isInitialized) {
        _processFrame();
      }
    });
  }
  
  Future<void> _processFrame() async {
    if (_isProcessing || _controller == null) {
      _startFrameProcessing();
      return;
    }
    
    setState(() => _isProcessing = true);
    
    try {
      // Capture image
      final image = await _controller!.takePicture();
      final imageFile = File(image.path);
      
      // Send to backend
      final response = await _service.detectChairActivity(
        imageFile,
        cameraId: 'mobile_camera_1',
      );
      
      setState(() {
        _lastResponse = response;
        _isProcessing = false;
      });
      
      // Clean up temporary image
      await imageFile.delete();
    } catch (e) {
      print('Error processing frame: $e');
      setState(() => _isProcessing = false);
    }
    
    // Continue processing
    _startFrameProcessing();
  }
  
  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    if (_controller == null || !_controller!.value.isInitialized) {
      return Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }
    
    return Scaffold(
      body: Stack(
        children: [
          // Camera preview
          CameraPreview(_controller!),
          
          // Overlay with chair statuses
          if (_lastResponse != null)
            _buildOverlay(_lastResponse!),
          
          // Processing indicator
          if (_isProcessing)
            Positioned(
              top: 40,
              right: 20,
              child: Container(
                padding: EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                      ),
                    ),
                    SizedBox(width: 8),
                    Text(
                      'Processing...',
                      style: TextStyle(color: Colors.white, fontSize: 12),
                    ),
                  ],
                ),
              ),
            ),
        ],
      ),
    );
  }
  
  Widget _buildOverlay(FrameInferenceResponse response) {
    final size = MediaQuery.of(context).size;
    final cameraSize = _controller!.value.previewSize!;
    final scaleX = size.width / cameraSize.height;
    final scaleY = size.height / cameraSize.width;
    
    return CustomPaint(
      painter: ChairOverlayPainter(
        chairs: response.chairs,
        scaleX: scaleX,
        scaleY: scaleY,
      ),
      child: Container(),
    );
  }
}

/// Custom painter for drawing chair bounding boxes
class ChairOverlayPainter extends CustomPainter {
  final List<ChairStatus> chairs;
  final double scaleX;
  final double scaleY;
  
  ChairOverlayPainter({
    required this.chairs,
    required this.scaleX,
    required this.scaleY,
  });
  
  @override
  void paint(Canvas canvas, Size size) {
    for (var chair in chairs) {
      final bbox = chair.bbox;
      final x1 = bbox[0] * scaleX;
      final y1 = bbox[1] * scaleY;
      final x2 = bbox[2] * scaleX;
      final y2 = bbox[3] * scaleY;
      
      // Draw bounding box
      final paint = Paint()
        ..color = Color(chair.getStatusColor())
        ..style = PaintingStyle.stroke
        ..strokeWidth = 3.0;
      
      canvas.drawRect(
        Rect.fromLTRB(x1, y1, x2, y2),
        paint,
      );
      
      // Draw label
      final textPainter = TextPainter(
        text: TextSpan(
          text: '${chair.chairId}: ${chair.status}\n${(chair.confidence * 100).toStringAsFixed(0)}%',
          style: TextStyle(
            color: Color(chair.getStatusColor()),
            fontSize: 14,
            fontWeight: FontWeight.bold,
            shadows: [
              Shadow(
                color: Colors.black,
                blurRadius: 4,
              ),
            ],
          ),
        ),
        textDirection: TextDirection.ltr,
      );
      textPainter.layout();
      textPainter.paint(canvas, Offset(x1, y1 - textPainter.height - 5));
    }
  }
  
  @override
  bool shouldRepaint(ChairOverlayPainter oldDelegate) {
    return chairs != oldDelegate.chairs;
  }
}
```

### **Step 4: Alternative - Using Annotated Image**

If you prefer to use the backend-annotated image instead of drawing overlays:

```dart
Future<void> _processFrameAnnotated() async {
  if (_isProcessing || _controller == null) return;
  
  setState(() => _isProcessing = true);
  
  try {
    final image = await _controller!.takePicture();
    final imageFile = File(image.path);
    
    // Get annotated image from backend
    final annotatedBytes = await _service.getAnnotatedFrame(
      imageFile,
      cameraId: 'mobile_camera_1',
    );
    
    // Save and display annotated image
    final tempDir = await getTemporaryDirectory();
    final annotatedFile = File('${tempDir.path}/annotated_${DateTime.now().millisecondsSinceEpoch}.jpg');
    await annotatedFile.writeAsBytes(annotatedBytes);
    
    // Display the annotated image
    setState(() {
      _annotatedImagePath = annotatedFile.path;
      _isProcessing = false;
    });
    
    await imageFile.delete();
  } catch (e) {
    print('Error: $e');
    setState(() => _isProcessing = false);
  }
}
```

---

## 🎨 UI Features You Can Build

### **1. Real-Time Status Display**
- Show chair statuses as colored overlays on camera preview
- Display confidence scores
- Show processing time

### **2. Status Summary**
- Count of RED/ORANGE/GREEN chairs
- Total chairs detected
- Average confidence

### **3. Historical Tracking**
- Store status changes over time
- Show activity timeline
- Generate reports

### **4. Settings**
- Adjust frame processing rate (FPS)
- Change server URL
- Toggle overlay display
- Adjust confidence thresholds

---

## 🔧 Configuration

### **Server URL**
Update the base URL in your service:

```dart
ChairDetectionService(
  baseUrl: 'http://192.168.1.100:8000', // Your server's IP address
);
```

### **Frame Rate**
Adjust processing frequency:

```dart
// Process every 200ms = ~5 FPS
Future.delayed(Duration(milliseconds: 200), () {
  _processFrame();
});

// Process every 100ms = ~10 FPS
Future.delayed(Duration(milliseconds: 100), () {
  _processFrame();
});
```

### **Image Quality**
Adjust camera resolution:

```dart
CameraController(
  _cameras![0],
  ResolutionPreset.low,    // Fastest, lowest quality
  ResolutionPreset.medium, // Balanced (recommended)
  ResolutionPreset.high,   // Slower, higher quality
);
```

---

## 📊 Response Format

### **JSON Response Example**

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

### **Status Meanings**
- **RED**: Chair is empty (no person detected)
- **ORANGE**: Person is sitting but hands are NOT on table
- **GREEN**: Person is sitting AND hands are ON table (productive state)

---

## 🚀 Next Steps

1. **Test the integration** with sample images
2. **Optimize frame rate** based on your device performance
3. **Add error handling** for network issues
4. **Implement caching** for offline scenarios
5. **Add analytics** to track chair usage patterns

---

## 📝 Notes

- **Network**: Ensure your mobile device and server are on the same network (or use ngrok for remote access)
- **Performance**: Lower resolution = faster processing
- **Battery**: Continuous processing will drain battery - consider adding pause/resume functionality
- **Privacy**: All processing happens on your server - no data is stored

---

## 🐛 Troubleshooting

### **Connection Issues**
- Check server is running: `curl http://localhost:8000/health`
- Verify IP address is correct
- Check firewall settings

### **Slow Processing**
- Reduce camera resolution
- Increase frame delay (lower FPS)
- Use lower quality images

### **No Detections**
- Ensure good lighting
- Check camera focus
- Verify objects are clearly visible

---

**Happy coding! 🎉**
