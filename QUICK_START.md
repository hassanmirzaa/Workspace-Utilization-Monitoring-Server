# 🚀 Quick Start Guide

## ✅ **Color Logic Confirmed**

- **🔴 RED**: Chair detected, **NO person sitting**
- **🟢 GREEN**: Person sitting **AND hands ON table**
- **🟠 ORANGE**: Person sitting **BUT hands NOT on table**

---

## 🏃 **Start Server on Localhost**

```bash
cd backend
python -m app.main
```

Server will be available at: **http://localhost:8000**

---

## 📡 **Available APIs**

### **1. Health Check**
```bash
curl http://localhost:8000/health
```

### **2. Process Image (JSON)**
```bash
curl -X POST "http://localhost:8000/infer/frame" \
  -F "file=@your_image.jpg"
```

### **3. Process Image (Annotated)**
```bash
curl -X POST "http://localhost:8000/infer/frame/annotated" \
  -F "file=@your_image.jpg" \
  -o output_annotated.jpg
```

### **4. Process Video (JSON)**
```bash
curl -X POST "http://localhost:8000/infer/video" \
  -F "file=@your_video.mp4" \
  -F "process_fps=2.0"
```

### **5. Process Video (Annotated)**
```bash
curl -X POST "http://localhost:8000/infer/video/annotated" \
  -F "file=@your_video.mp4" \
  -F "process_fps=2.0" \
  -o output_annotated.mp4
```

---

## 🧪 **Test Script**

```bash
cd backend
python test_api.py [image_path] [video_path]
```

Example:
```bash
python test_api.py test.jpg test.mp4
```

---

## 📱 **Mobile App Integration**

Your Flutter app can:
1. **Upload video** → Use `/infer/video` or `/infer/video/annotated`
2. **Record video** → Save to file, then upload
3. **Process frames** → Use `/infer/frame` for real-time processing

See `FLUTTER_INTEGRATION.md` for complete code examples.

---

## 🌐 **Access from Mobile Device**

1. Find your computer's IP:
   ```bash
   # macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Windows
   ipconfig
   ```

2. Use in Flutter app:
   ```dart
   ChairDetectionService(
     baseUrl: 'http://YOUR_IP:8000',  // e.g., 'http://192.168.1.100:8000'
   );
   ```

---

## 📊 **API Documentation**

Once server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ✅ **All APIs are Live and Ready!**

The server is configured to:
- ✅ Listen on `0.0.0.0:8000` (accessible from network)
- ✅ Process images and videos
- ✅ Return colored annotations (RED/ORANGE/GREEN)
- ✅ Handle multiple chairs per frame
- ✅ Work with Flutter mobile app

**Start the server and test! 🎉**
