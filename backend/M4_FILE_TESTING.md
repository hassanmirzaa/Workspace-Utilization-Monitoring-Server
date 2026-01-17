# Testing with M4 Files (M4V)

## ✅ M4V Support Added

The API now supports **M4V files** (and other video formats) directly! You can upload `.m4v` files just like MP4 files.

---

## 🚀 Quick Test with M4V Files

### **Option 1: Direct Upload (Recommended)**

Just upload your `.m4v` file directly to the API - it will work automatically!

**In Swagger UI:**
1. Go to http://localhost:8000/docs
2. Select **POST** `/infer/video` or `/infer/video/annotated`
3. Click "Try it out"
4. Upload your `.m4v` file
5. Click "Execute"

**Using curl:**
```bash
curl -X POST "http://localhost:8000/infer/video/annotated" \
  -F "file=@your_video.m4v" \
  -F "process_fps=2.0" \
  -o output_annotated.mp4
```

---

## 📋 Supported Video Formats

The API now supports:
- ✅ **MP4** (.mp4)
- ✅ **M4V** (.m4v) - **NEW!**
- ✅ **AVI** (.avi)
- ✅ **MOV** (.mov)
- ✅ **MKV** (.mkv)
- ✅ **WMV** (.wmv)
- ✅ Any format supported by OpenCV

---

## 🧪 Testing Steps

### **1. Start Server**
```bash
cd backend
python -m app.main
```

### **2. Test with M4V File**

**Method A: Swagger UI (Easiest)**
1. Open http://localhost:8000/docs
2. Find **POST** `/infer/video/annotated`
3. Click "Try it out"
4. Upload your `.m4v` file
5. Set `process_fps` to `2.0` (or lower for faster processing)
6. Click "Execute"
7. Download the annotated video

**Method B: Using curl**
```bash
# Test with M4V file
curl -X POST "http://localhost:8000/infer/video" \
  -F "file=@test_video.m4v" \
  -F "process_fps=2.0"
```

**Method C: Using Python**
```python
import requests

url = "http://localhost:8000/infer/video/annotated"
with open("test_video.m4v", "rb") as f:
    files = {"file": ("test.m4v", f, "video/x-m4v")}
    data = {"process_fps": "2.0"}
    response = requests.post(url, files=files, data=data)

with open("output_annotated.mp4", "wb") as f:
    f.write(response.content)
```

---

## 🔄 Converting M4V to MP4 (Optional)

If you prefer to convert M4V to MP4 first (not required, but sometimes helpful):

### **Using FFmpeg (Recommended)**
```bash
# Install FFmpeg (if not installed)
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
# Windows: Download from https://ffmpeg.org

# Convert M4V to MP4
ffmpeg -i input.m4v -c copy output.mp4

# Or re-encode (if codec issues)
ffmpeg -i input.m4v -c:v libx264 -c:a aac output.mp4
```

### **Using Python (moviepy)**
```python
from moviepy.editor import VideoFileClip

clip = VideoFileClip("input.m4v")
clip.write_videofile("output.mp4", codec='libx264')
clip.close()
```

**Note:** Conversion is **NOT required** - the API handles M4V files directly!

---

## 🎯 What Happens with M4V Files

1. **Upload**: Your `.m4v` file is uploaded to the server
2. **Detection**: Server detects the `.m4v` extension
3. **Processing**: OpenCV processes the M4V file (same as MP4)
4. **Output**: Returns annotated video (as MP4) or JSON results

---

## ⚙️ Performance Tips

- **Lower `process_fps`** for faster processing (1.0-2.0 recommended)
- **Smaller files** process faster
- **M4V files** process at the same speed as MP4 files

---

## 🐛 Troubleshooting

### **M4V File Not Processing**

1. **Check file format**: Ensure it's a valid video file
   ```bash
   file your_video.m4v
   ```

2. **Try converting**: If OpenCV can't read it, convert first:
   ```bash
   ffmpeg -i input.m4v -c:v libx264 -c:a aac output.mp4
   ```

3. **Check file size**: Very large files may timeout
   - Try a shorter clip first
   - Reduce `process_fps` to speed up

### **Error: "Failed to open video file"**

- The M4V file might use a codec OpenCV doesn't support
- Solution: Convert to MP4 using FFmpeg (see above)

---

## ✅ Quick Test Command

```bash
# Test with your M4V file
curl -X POST "http://localhost:8000/infer/video/annotated" \
  -F "file=@your_video.m4v" \
  -F "process_fps=2.0" \
  -o test_output.mp4
```

---

## 📝 Example: Testing Multiple M4V Files

```bash
# Test all M4V files in a directory
for file in *.m4v; do
    echo "Processing $file..."
    curl -X POST "http://localhost:8000/infer/video/annotated" \
      -F "file=@$file" \
      -F "process_fps=2.0" \
      -o "${file%.m4v}_annotated.mp4"
done
```

---

**M4V files are now fully supported! Just upload and test! 🎉**
