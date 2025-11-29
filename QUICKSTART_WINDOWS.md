# Quick Start Guide for Windows

This guide will help you get the Drone Trajectory System running on Windows in just a few minutes.

## Prerequisites

Before you begin, make sure you have:

1. **Python 3.8 or higher** - [Download](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   
2. **Visual Studio 2017 or later** (for C++ components) - [Download](https://visualstudio.microsoft.com/downloads/)
   - Install "Desktop development with C++" workload
   - Community Edition is free
   
3. **CMake 3.15 or higher** (for C++ components) - [Download](https://cmake.org/download/)
   - During installation, select "Add CMake to system PATH"

## Method 1: Automatic Setup (Recommended)

### Step 1: Open PowerShell

Right-click on the Start menu and select "Windows PowerShell" or "Terminal"

### Step 2: Navigate to the project

```powershell
cd C:\path\to\workspace
```

### Step 3: Run the demo script

```powershell
.\run_demo.ps1
```

**That's it!** The script will:
- ✓ Check dependencies
- ✓ Download and set up ONNX Runtime automatically
- ✓ Generate training data
- ✓ Train the model
- ✓ Export to ONNX format
- ✓ Build C++ components
- ✓ Run the demo

### Troubleshooting

If you get an error about script execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\run_demo.ps1
```

## Method 2: Manual Setup

If you prefer to run steps individually:

### Step 1: Install Python Dependencies

```powershell
pip install -r requirements.txt
```

### Step 2: Set up ONNX Runtime

```powershell
.\setup_onnx_windows.ps1
```

Or use the batch file:

```batch
setup_onnx_windows.bat
```

### Step 3: Generate Data and Train Model

```powershell
cd python
python data_generator.py
python train_model.py
python export_to_onnx.py
cd ..
```

### Step 4: Build C++ Components

```powershell
cd cpp
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
cmake --build . --config Release
cd ..\..
```

### Step 5: Run the Demo

```powershell
cd cpp\build\Release
.\drone_trajectory_cpp.exe
```

## Method 3: Python Only (No C++ Build)

If you don't want to build C++ components:

```powershell
cd python
python data_generator.py
python train_model.py
python simulation.py
```

## What You Should See

### Python Training
```
Epoch [1/50] Loss: 0.0234
Epoch [2/50] Loss: 0.0198
...
Model saved to: models/best_model.pth
```

### ONNX Export
```
Model exported to: models/drone_trajectory.onnx
ONNX model verified successfully
```

### C++ Demo
```
Drone Trajectory Predictor - C++ Demo
=====================================

Loading model from: ../../../../models/drone_trajectory.onnx
✓ Model loaded successfully

Running trajectory prediction...
Predicted position: [2.34, 1.56, 5.78]
Inference time: 0.8 ms
```

## Directory Structure

After successful setup:

```
workspace/
├── onnxruntime-win-x64-1.17.1/     # Auto-downloaded
│   ├── include/
│   └── lib/
├── data/
│   └── train_data.pkl               # Generated
├── models/
│   ├── best_model.pth               # Generated
│   ├── drone_trajectory.onnx        # Generated
│   └── drone_trajectory_normalization.txt
├── python/
│   └── *.py
├── cpp/
│   ├── build/
│   │   └── Release/
│   │       └── drone_trajectory_cpp.exe
│   └── *.cpp, *.h
├── run_demo.ps1                     # Main demo script
└── setup_onnx_windows.ps1           # ONNX Runtime setup
```

## Common Issues

### Issue 1: Python not found

**Error:** `python: The term 'python' is not recognized`

**Solution:**
- Install Python from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation
- Restart PowerShell after installation

### Issue 2: CMake not found

**Error:** `cmake: The term 'cmake' is not recognized`

**Solution:**
- Install CMake from https://cmake.org/download/
- Select "Add CMake to system PATH" during installation
- Restart PowerShell after installation

### Issue 3: Visual Studio not detected

**Error:** `No Visual Studio detected`

**Solution:**
- Install Visual Studio from https://visualstudio.microsoft.com/downloads/
- Make sure to install "Desktop development with C++" workload
- Use Developer Command Prompt for VS instead of regular PowerShell

### Issue 4: ONNX Runtime download fails

**Error:** `Failed to download ONNX Runtime`

**Solution:**
- Check your internet connection
- Try downloading manually:
  1. Go to: https://github.com/microsoft/onnxruntime/releases
  2. Download: `onnxruntime-win-x64-1.17.1.zip`
  3. Extract to workspace directory

### Issue 5: "onnxruntime.dll not found"

**Error:** Application fails to run with DLL error

**Solution:**
- The DLL should be auto-copied by CMake
- If not, manually copy: `onnxruntime-win-x64-1.17.1\lib\onnxruntime.dll`
- To: `cpp\build\Release\`

## Next Steps

### Run Interactive Simulation

```powershell
cd python
python simulation.py
```

This opens a PyQt5 GUI with real-time trajectory visualization.

### Test Different Scenarios

Edit `python/data_generator.py` to change:
- Number of training samples
- Drone behavior parameters
- Mission complexity

Then retrain:

```powershell
cd python
python data_generator.py
python train_model.py
python export_to_onnx.py
```

### Integrate with Your Project

See `cpp/README_WINDOWS.md` for detailed instructions on:
- Using the C++ library in your project
- API documentation
- Advanced configuration
- Performance optimization

## Performance Expectations

On a typical Windows laptop:

| Component | Time |
|-----------|------|
| Data Generation | ~30 seconds |
| Model Training | ~2-5 minutes |
| ONNX Export | ~5 seconds |
| C++ Build | ~1-2 minutes |
| C++ Inference | < 1ms per prediction |

Total first-time setup: **~10 minutes**

## Additional Resources

- **Main README:** `README.md` - Project overview and features
- **C++ Guide:** `cpp/README_WINDOWS.md` - Detailed C++ build instructions
- **Python Docs:** `python/*.py` - Documented Python source code
- **Usage Examples:** `USAGE_EXAMPLES.md` - More usage scenarios

## Getting Help

If you encounter issues:

1. Check this guide first
2. Review `cpp/README_WINDOWS.md` for C++ specific issues
3. Make sure all prerequisites are installed
4. Try a clean rebuild:
   ```powershell
   Remove-Item -Recurse -Force cpp\build
   Remove-Item -Recurse -Force models
   Remove-Item -Recurse -Force data
   .\run_demo.ps1
   ```

## Success Checklist

- [x] Python 3.8+ installed and in PATH
- [x] Visual Studio with C++ workload installed
- [x] CMake installed and in PATH
- [x] `run_demo.ps1` runs without errors
- [x] ONNX Runtime downloaded and extracted
- [x] Training data generated
- [x] Model trained and exported to ONNX
- [x] C++ executable built successfully
- [x] Demo runs and shows predictions

**Congratulations!** 🎉 You're all set to use the Drone Trajectory System on Windows!
