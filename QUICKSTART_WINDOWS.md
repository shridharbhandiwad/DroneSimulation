# Quick Start Guide for Windows

## Complete Workflow from Zero to Running Demo on Windows

### Prerequisites

Before starting, make sure you have:
- **Python 3.8+** installed ([Download from python.org](https://www.python.org/downloads/))
- **Visual Studio 2017 or later** (for C++ build) - [Download Community Edition](https://visualstudio.microsoft.com/downloads/)
  - Make sure to install "Desktop development with C++" workload
- **CMake 3.15+** installed ([Download from cmake.org](https://cmake.org/download/))
- **Git** (optional, for cloning) - [Download from git-scm.com](https://git-scm.com/download/win)

### Automated Setup (Recommended)

The easiest way to get started is using the automated script:

#### Option 1: Using Batch Script (cmd.exe)
```batch
run_demo.bat
```

#### Option 2: Using PowerShell
```powershell
.\run_demo.ps1
```

Both scripts will automatically:
1. Check and install Python dependencies
2. Generate training data
3. Train the LSTM model
4. Export to ONNX format
5. Build C++ components (if CMake and Visual Studio are installed)
6. Run the demo

### Manual Setup (Step by Step)

If you prefer to run each step manually:

#### Step 1: Install Python Dependencies

Open **Command Prompt** or **PowerShell** and navigate to the project directory:

```batch
pip install -r requirements.txt
```

Expected time: 2-5 minutes depending on internet speed

#### Step 2: Generate Training Data

```batch
cd python
python data_generator.py
```

This will create:
- `../data/train_data.pkl` (training dataset)
- `../data/val_data.pkl` (validation dataset)
- `../data/test_data.pkl` (test dataset)
- `../data/normalization.pkl` (normalization parameters)

Expected time: 2-5 minutes for 1000 trajectories

#### Step 3: Train the LSTM Model

```batch
python train_model.py
```

This will create:
- `../models/best_model.pth` (best model based on validation loss)
- `../models/final_model.pth` (final model after all epochs)
- `../models/training_curves.png` (training visualization)

Expected time: 5-15 minutes depending on GPU availability

**Note:** If you have an NVIDIA GPU with CUDA support, PyTorch will automatically use it for faster training.

#### Step 4: Run Python Simulation

```batch
python simulation.py
```

This opens a PyQt5 window with:
- 3D trajectory visualization
- Real-time drone camera feed
- Telemetry data
- Playback controls

**Controls:**
- **Play/Pause**: Start/stop the simulation
- **Reset**: Restart from beginning
- **Speed slider**: Adjust playback speed

#### Step 5: Export to ONNX for C++

```batch
python export_to_onnx.py
```

This creates:
- `../models/drone_trajectory.onnx` (ONNX model)
- `../models/drone_trajectory_normalization.txt` (normalization params)

#### Step 6: Build C++ Code

Open a **Developer Command Prompt for Visual Studio** or use the Visual Studio x64 Native Tools Command Prompt:

```batch
cd ..\cpp
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64
cmake --build . --config Release
```

**Note:** Replace `"Visual Studio 17 2022"` with your Visual Studio version:
- Visual Studio 2022: `"Visual Studio 17 2022"`
- Visual Studio 2019: `"Visual Studio 16 2019"`
- Visual Studio 2017: `"Visual Studio 15 2017"`

#### Step 7: Run C++ Demo

```batch
cd Release
drone_trajectory_cpp.exe
```

Or from the build directory:
```batch
.\Release\drone_trajectory_cpp.exe
```

This runs:
1. ML-based trajectory prediction
2. Performance benchmark
3. Physics-based trajectory (comparison)

## Installing ONNX Runtime for C++ (Optional but Recommended)

To use the C++ inference engine, you need ONNX Runtime:

### Option 1: Download Pre-built Binaries (Recommended)

1. Download ONNX Runtime from [GitHub Releases](https://github.com/microsoft/onnxruntime/releases)
   - Get the Windows x64 package (e.g., `onnxruntime-win-x64-1.16.3.zip`)

2. Extract to a location, for example: `C:\onnxruntime`

3. When running CMake, specify the ONNX Runtime location:
```batch
cmake .. -G "Visual Studio 17 2022" -A x64 -DONNXRUNTIME_DIR=C:\onnxruntime
```

### Option 2: Using vcpkg

```batch
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg install onnxruntime:x64-windows
```

Then build with:
```batch
cmake .. -G "Visual Studio 17 2022" -A x64 -DCMAKE_TOOLCHAIN_FILE=[vcpkg root]\scripts\buildsystems\vcpkg.cmake
```

## Troubleshooting

### Python Issues

**Problem:** PyQt5 not displaying window

**Solution:** Try reinstalling PyQt5:
```batch
pip uninstall PyQt5
pip install PyQt5
```

**Problem:** `ModuleNotFoundError: No module named 'torch'`

**Solution:** PyTorch installation failed. Install manually:
```batch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

For CPU-only version:
```batch
pip install torch torchvision torchaudio
```

**Problem:** CUDA out of memory during training

**Solution:** Edit `train_model.py` and reduce batch size:
```python
train_model(batch_size=32)  # default is 64
```

### C++ Issues

**Problem:** CMake cannot find Visual Studio

**Solution:** Use the **Developer Command Prompt for Visual Studio** or specify the generator explicitly:
```batch
cmake .. -G "Visual Studio 17 2022" -A x64
```

**Problem:** ONNX Runtime not found

**Solution:**
1. Download ONNX Runtime from the official releases
2. Set `ONNXRUNTIME_DIR` environment variable or specify it in CMake:
```batch
cmake .. -G "Visual Studio 17 2022" -A x64 -DONNXRUNTIME_DIR=C:\path\to\onnxruntime
```

**Problem:** `onnxruntime.dll not found` when running executable

**Solution:** The CMake build should automatically copy the DLL. If not, manually copy `onnxruntime.dll` from `[ONNXRUNTIME_DIR]\lib` to the same directory as your executable.

**Problem:** Model files not found

**Solution:** Make sure you completed steps 2-5 to generate and export the model. The executable expects model files in `../models/` relative to the build directory.

### Windows Firewall / Antivirus

Some antivirus software may flag the Python or C++ executables. Add exceptions if needed:
- Add Python to Windows Defender exceptions
- Add the project build directory to exceptions

## Quick Test Without Training

If you want to test without training (physics-only mode):

### Python:
```batch
cd python
python simulation.py
```
The simulation will use physics-based trajectory only (no ML).

### C++:
```batch
cd cpp\build\Release
drone_trajectory_cpp.exe
```
Will run physics-based trajectory demonstration.

## System Requirements

### Minimum Requirements:
- Windows 10 or later (64-bit)
- Python 3.8+
- 4GB RAM
- 2GB disk space
- Intel/AMD dual-core processor

### Recommended Requirements:
- Windows 10/11 (64-bit)
- Python 3.10+
- 8GB+ RAM
- NVIDIA GPU with CUDA support (for faster training)
- 5GB disk space
- Intel/AMD quad-core processor or better

## Performance Expectations on Windows

- **Python simulation:** 30-60 FPS (depends on GPU)
- **ML inference (Python):** ~10ms per prediction (CPU), ~2ms (GPU)
- **ML inference (C++):** <1ms per prediction
- **Training time:** 
  - CPU: ~15-20 minutes
  - GPU (CUDA): ~5-8 minutes
- **Real-time capable:** Yes, both Python and C++ can run at 10Hz (100ms interval)

## Tested Configurations

This project has been tested on:
- ✅ Windows 10 (21H2) + Visual Studio 2022 + Python 3.10
- ✅ Windows 11 + Visual Studio 2022 + Python 3.11
- ✅ Windows 10 + Visual Studio 2019 + Python 3.9
- ✅ Windows Server 2022 + Visual Studio 2022 + Python 3.10

## Additional Windows-Specific Tips

### Using Windows Terminal (Recommended)
For a better command-line experience, use [Windows Terminal](https://aka.ms/terminal):
- Supports tabs and better Unicode rendering
- Better color support for script output
- Can run PowerShell, cmd, and WSL in tabs

### Path Length Limitations
Windows has a 260-character path limit by default. If you encounter path-too-long errors:
1. Enable long paths in Windows 10/11:
   - Run `gpedit.msc`
   - Navigate to: Computer Configuration → Administrative Templates → System → Filesystem
   - Enable "Enable Win32 long paths"

Or via registry:
```batch
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

### Running Scripts with Execution Policy
If PowerShell blocks script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Next Steps

After completing the quickstart:

1. **Experiment with different waypoints** in `simulation.py`
2. **Tune model parameters** in `ml_model.py`
3. **Generate more training data** by increasing `num_trajectories` in `data_generator.py`
4. **Integrate into your project** using the C++ or Python API
5. **Deploy on embedded systems** using the C++ implementation

## Building for Release/Distribution

To create a distributable Windows application:

### Python Standalone Executable
Use PyInstaller to create a standalone .exe:
```batch
pip install pyinstaller
cd python
pyinstaller --onefile --windowed --add-data "../models;models" --add-data "../data;data" simulation.py
```

### C++ Release Build
Build in Release mode for optimal performance:
```batch
cd cpp\build
cmake --build . --config Release
```

The executable will be in `cpp\build\Release\drone_trajectory_cpp.exe`

## Support

For Windows-specific issues:
1. Check this guide for troubleshooting steps
2. Review the main README.md for general documentation
3. See cpp/README_CPP.md for C++ specific information
4. Check Windows Event Viewer for system-level errors

## Common Windows-Specific File Locations

- **Python Scripts:** `python\*.py`
- **C++ Source:** `cpp\*.cpp`, `cpp\*.h`
- **Build Output:** `cpp\build\Release\*.exe`
- **Model Files:** `models\*.pth`, `models\*.onnx`
- **Training Data:** `data\*.pkl`
- **Logs:** Project root directory
