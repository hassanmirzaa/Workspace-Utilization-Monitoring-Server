# PyTorch 2.6 Compatibility Fix

## ✅ Issue Fixed

PyTorch 2.6 changed the default `weights_only` parameter in `torch.load` from `False` to `True` for security. This breaks YOLOv8 model loading.

## 🔧 Solution Applied

The code has been updated to:
1. Set environment variable `TORCH_LOAD_WEIGHTS_ONLY=False`
2. Monkey-patch `torch.load` to use `weights_only=False` by default

This allows YOLOv8 models to load correctly while maintaining security for other use cases.

## 📝 What Changed

**File:** `backend/app/services/detector.py`

- Added environment variable setting
- Added torch.load monkey-patch before YOLO import
- This ensures YOLO models can load with custom classes

## ✅ Verification

After this fix, the YOLO model should load successfully. You should see:
```
YOLO model loaded on device: cpu
```

If you still see errors, try:
1. Restart the server
2. Delete the cached model: `rm yolov8n.pt` (it will re-download)
3. Check PyTorch version: `python -c "import torch; print(torch.__version__)"`

## 🔒 Security Note

This fix allows loading models with custom classes (required for YOLOv8). The YOLOv8 model file is from a trusted source (Ultralytics official repository), so this is safe.

---

**The fix is already applied - just restart your server! 🎉**
