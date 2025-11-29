# ONNX Export - Quick Fix Reference

## ⚡ TL;DR

The ONNX export error has been **FIXED**. Just pull the latest changes and run:

```bash
python python/export_to_onnx.py
```

---

## 🔧 What Was Changed

| File | Change | Why |
|------|--------|-----|
| `python/export_to_onnx.py` | `opset_version=17` | Avoid version conversion errors |
| `python/export_to_onnx.py` | `do_constant_folding=False` | Avoid optimization bug |
| `ARCHITECTURE.md` | Updated docs | Reflect changes |

---

## ✅ Verify Setup (Optional)

```bash
python python/check_onnx_setup.py
```

This checks:
- ✓ PyTorch installed
- ✓ ONNX installed
- ✓ ONNX Runtime installed
- ✓ Versions compatible
- ✓ Simple export test

---

## 📋 Quick Commands

### 1. Check Setup
```bash
cd python
python check_onnx_setup.py
```

### 2. Export Model
```bash
python export_to_onnx.py
```

### 3. Verify Export
```bash
python -c "import onnx; onnx.checker.check_model(onnx.load('../models/drone_trajectory.onnx')); print('✓ Valid!')"
```

---

## 🆘 Still Having Issues?

### Error: Version 18 for Split
**Status**: ✅ Fixed (use opset 17)

### Error: 'NoneType' object has no attribute 'ndim'
**Status**: ✅ Fixed (constant folding disabled)

### Error: ONNX Runtime doesn't support opset 17
**Solution**: Update ONNX Runtime
```bash
pip install --upgrade onnxruntime
```

### Error: Module not found
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

---

## 📚 Full Documentation

- **Complete Guide**: [ONNX_FIX_SUMMARY.md](ONNX_FIX_SUMMARY.md)
- **Technical Details**: [ONNX_EXPORT_FIX.md](ONNX_EXPORT_FIX.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Main README**: [README.md](README.md)

---

## 🎯 Expected Output

When export succeeds, you'll see:

```
Loading PyTorch model...
Model loaded from ../models/best_model.pth

Exporting to ONNX...
Model successfully exported to ../models/drone_trajectory.onnx

Verifying ONNX model...
ONNX model is valid!

Testing ONNX inference...
ONNX inference successful!
✓ ONNX model matches PyTorch model!
```

---

## 📦 Output Files

After successful export:

- `models/drone_trajectory.onnx` - ONNX model (~500 KB)
- `models/drone_trajectory_normalization.txt` - Normalization params for C++

---

**Status**: ✅ **FIXED - Ready to Use**

Last Updated: 2025-11-29
