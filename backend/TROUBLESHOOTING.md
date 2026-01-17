# Troubleshooting Guide

## Protobuf/TensorFlow Conflict with MediaPipe

If you encounter this error:
```
ImportError: cannot import name 'runtime_version' from 'google.protobuf'
```

This is caused by a version conflict between:
- **MediaPipe 0.10.7** requires `protobuf<4,>=3.11`
- **TensorFlow 2.20.0** requires `protobuf>=5.28.0`

### Solution 1: Uninstall TensorFlow (Recommended)

Since this project doesn't use TensorFlow, uninstall it:

```bash
pip uninstall tensorflow
```

Then restart the server.

### Solution 2: Use a Virtual Environment

Create an isolated environment:

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

pip install -r requirements.txt
```

### Solution 3: Upgrade Protobuf (May Break MediaPipe)

⚠️ **Warning**: This may break MediaPipe if protobuf version is incompatible.

```bash
pip install --upgrade "protobuf>=4.21.0,<5.0.0"
```

If MediaPipe fails after this, revert:
```bash
pip install "protobuf==3.20.3"
```

### Solution 4: Use Newer MediaPipe Version

Try upgrading MediaPipe to a version that doesn't have TensorFlow dependencies:

```bash
pip install --upgrade mediapipe
```

Note: Newer versions may have API changes.

## Quick Fix

The fastest solution is usually:

```bash
pip uninstall tensorflow
python -m app.main
```
