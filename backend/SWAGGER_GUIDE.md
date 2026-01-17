# 📚 Swagger UI Testing Guide

## 🚀 Access Swagger UI

Once your server is running, access Swagger UI at:

**http://localhost:8000/docs**

---

## 📡 All Available Endpoints in Swagger

### **1. Health Check**
- **GET** `/health`
- Test if server is running
- No parameters needed
- Click "Try it out" → "Execute"

### **2. Process Image (JSON)**
- **POST** `/infer/frame`
- Upload an image file
- Get JSON response with chair statuses
- **Parameters:**
  - `file`: Choose image file (JPEG/PNG)
  - `camera_id`: Optional text field

### **3. Process Image (Annotated)**
- **POST** `/infer/frame/annotated`
- Upload an image file
- Get annotated image with colored boxes
- **Parameters:**
  - `file`: Choose image file (JPEG/PNG)
  - `camera_id`: Optional text field

### **4. Process Video (JSON)**
- **POST** `/infer/video`
- Upload a video file
- Get JSON response with frame-by-frame results
- **Parameters:**
  - `file`: Choose video file (MP4/AVI/MOV)
  - `camera_id`: Optional text field
  - `process_fps`: Number (default: 2.0)

### **5. Process Video (Annotated)**
- **POST** `/infer/video/annotated`
- Upload a video file
- Get annotated video with colored boxes
- **Parameters:**
  - `file`: Choose video file (MP4/AVI/MOV)
  - `camera_id`: Optional text field
  - `process_fps`: Number (default: 2.0)

---

## 🧪 How to Test in Swagger UI

### **Step 1: Start Server**
```bash
cd backend
python -m app.main
```

### **Step 2: Open Swagger UI**
Open browser: **http://localhost:8000/docs**

### **Step 3: Test an Endpoint**

1. **Click on an endpoint** (e.g., `/infer/frame`)
2. **Click "Try it out"** button
3. **Fill in parameters:**
   - For file uploads: Click "Choose File" and select your image/video
   - For optional fields: Leave blank or fill in
4. **Click "Execute"**
5. **View results:**
   - JSON responses show in the "Response body" section
   - Images/videos can be downloaded or viewed

---

## 🎨 Color Legend (Shown in Swagger Descriptions)

- **🔴 RED**: Chair detected, no person sitting
- **🟠 ORANGE**: Person sitting, hands NOT on table
- **🟢 GREEN**: Person sitting, hands ON table

---

## 📝 Example Test Flow

### **Test Image Processing:**

1. Go to **POST** `/infer/frame`
2. Click "Try it out"
3. Upload a test image (JPEG/PNG)
4. Click "Execute"
5. View JSON response with chair statuses

### **Test Video Processing:**

1. Go to **POST** `/infer/video/annotated`
2. Click "Try it out"
3. Upload a test video (MP4)
4. Set `process_fps` to `2.0` (or lower for faster processing)
5. Click "Execute"
6. Download the annotated video from response

---

## 🔍 View API Schema

- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **ReDoc**: http://localhost:8000/redoc (alternative documentation)

---

## 💡 Tips

1. **Start with Health Check** - Verify server is running
2. **Use small test files first** - Faster testing
3. **Lower process_fps for videos** - Faster processing (1.0-2.0 recommended)
4. **Check response times** - Processing time shown in JSON responses
5. **Download annotated results** - Right-click on response to save

---

## 🐛 Troubleshooting

### **Swagger UI Not Loading**
- Ensure server is running: `python -m app.main`
- Check URL: http://localhost:8000/docs
- Check browser console for errors

### **File Upload Fails**
- Ensure file format is supported (JPEG/PNG for images, MP4/AVI/MOV for videos)
- Check file size (very large files may timeout)
- Try a smaller test file first

### **Slow Processing**
- For videos, reduce `process_fps` (try 1.0)
- Use smaller resolution images/videos
- Check server logs for errors

---

**All APIs are fully documented and testable in Swagger UI! 🎉**
