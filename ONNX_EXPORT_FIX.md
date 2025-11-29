# ONNX Export Fix

## Problem
The ONNX export was failing with the following errors:
1. Version conversion error: "No Adapter From Version 18 for Split"
2. Optimization error: "AttributeError: 'NoneType' object has no attribute 'ndim'"

## Root Cause
- The export script was using ONNX opset version 11
- PyTorch was generating operators from opset version 18
- The ONNX version converter doesn't support downgrading Split operator from v18 to v11
- The constant folding optimization in onnxscript has a bug when handling Split operations

## Solution Applied
Modified `python/export_to_onnx.py`:
1. **Changed opset_version from 11 to 17**
   - Opset 17 is modern and well-supported by ONNX Runtime
   - Avoids version conversion issues
   
2. **Disabled constant folding (do_constant_folding=False)**
   - Avoids the optimization bug in onnxscript
   - The model will still work correctly, just slightly less optimized

## Testing
Run the export script:
```bash
python python/export_to_onnx.py
```

The export should now complete successfully.

## Alternative Solutions (if needed)

### Option 1: Use opset 18 (latest)
If your ONNX Runtime supports opset 18, you can use:
```python
opset_version=18,
do_constant_folding=False,
```

### Option 2: Upgrade onnxscript
The bug might be fixed in newer versions:
```bash
pip install --upgrade onnxscript onnx torch
```

### Option 3: Use legacy export (PyTorch < 2.1)
If you need opset 11 specifically, use the legacy exporter:
```python
torch.onnx.export(
    ...,
    opset_version=11,
    export_params=True,
)
```
But set environment variable first:
```bash
export TORCH_ONNX_EXPERIMENTAL_RUNTIME_TYPE_CHECK=ERRORS
```

## ONNX Runtime Compatibility
- Opset 17 is supported by ONNX Runtime 1.14.0+
- Opset 18 is supported by ONNX Runtime 1.15.0+
- Most modern installations support these versions

## Verification
After successful export, the script will:
1. Verify the ONNX model structure
2. Test inference with ONNX Runtime
3. Compare outputs with PyTorch to ensure correctness
4. Save normalization parameters for C++ inference

## Files Generated
- `models/drone_trajectory.onnx` - The exported model
- `models/drone_trajectory_normalization.txt` - Normalization parameters for C++ inference
