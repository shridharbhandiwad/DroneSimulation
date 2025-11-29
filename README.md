# Drone Trajectory Generation and Simulation System

## Overview
This system generates drone trajectories using ML (LSTM) based on initial position, speed, and waypoints. It includes:
- **Trajectory Generation**: Physics-based + LSTM for smooth trajectory prediction
- **PyQt5 Simulation**: 3D visualization with camera feed
- **C++ Compatibility**: ONNX model export for real-time C++ inference

## Features
- Generate trajectory data at 100ms intervals
- LSTM-based trajectory prediction
- 3D visualization with PyQt5
- Simulated camera feed from drone perspective
- Export to ONNX for C++ integration
- Real-time C++ inference code

## Architecture

### Python Components
1. **trajectory_generator.py**: Physics-based trajectory generation
2. **ml_model.py**: LSTM model for trajectory prediction
3. **simulation.py**: PyQt5 3D visualization with camera feed
4. **data_generator.py**: Training data generation
5. **train_model.py**: Model training script
6. **export_to_onnx.py**: Model conversion to ONNX

### C++ Components
1. **drone_trajectory.h/cpp**: C++ trajectory predictor using ONNX Runtime
2. **CMakeLists.txt**: Build configuration

## Installation

### Python Setup

**Linux/macOS:**
```bash
pip install -r requirements.txt
```

**Windows:**
```batch
pip install -r requirements.txt
```

Or use the automated setup script:
```batch
setup_windows.bat
```

### C++ Setup

**Linux (Ubuntu/Debian):**
```bash
# Install ONNX Runtime
sudo apt-get install libonnxruntime-dev

# Or build from source:
# https://onnxruntime.ai/docs/build/inferencing.html
```

**Windows:**
1. Download ONNX Runtime from [GitHub Releases](https://github.com/microsoft/onnxruntime/releases)
2. Extract to `C:\onnxruntime` (or another location)
3. When building, specify the path:
```batch
cmake .. -G "Visual Studio 17 2022" -A x64 -DONNXRUNTIME_DIR=C:\onnxruntime
```

See [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md) for detailed Windows instructions.

## Usage

### Quick Start

**Linux/macOS:**
```bash
./run_demo.sh
```

**Windows (Batch):**
```batch
run_demo.bat
```

**Windows (PowerShell):**
```powershell
.\run_demo.ps1
```

### Manual Steps

#### 1. Generate Training Data
**Linux/macOS:**
```bash
python data_generator.py
```

**Windows:**
```batch
cd python
python data_generator.py
```

#### 2. Train the Model
**Linux/macOS:**
```bash
python train_model.py
```

**Windows:**
```batch
python train_model.py
```

#### 3. Run Simulation
**Linux/macOS:**
```bash
python simulation.py
```

**Windows:**
```batch
python simulation.py
```

#### 4. Export to ONNX
**Linux/macOS:**
```bash
python export_to_onnx.py
```

**Windows:**
```batch
python export_to_onnx.py
```

#### 5. Build and Run C++ Code

**Linux/macOS:**
```bash
cd cpp
mkdir build && cd build
cmake ..
make
./drone_trajectory_cpp
```

**Windows:**
```batch
cd cpp
mkdir build
cd build
cmake .. -G "Visual Studio 17 2022" -A x64
cmake --build . --config Release
.\Release\drone_trajectory_cpp.exe
```

## Model Details

### Input Features (per timestep)
- Position (x, y, z)
- Velocity (vx, vy, vz)
- Acceleration (ax, ay, az)
- Target waypoint (wx, wy, wz)
- Distance to waypoint
- Time since start

### Output
- Next position (x, y, z) at t+100ms
- Next velocity (vx, vy, vz)

### Architecture
- LSTM with 2 layers (128 hidden units)
- Sequence length: 10 timesteps (1 second history)
- Prediction: Next timestep (100ms ahead)

## File Structure
```
/workspace/
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── QUICKSTART.md                 # General quickstart guide
├── QUICKSTART_WINDOWS.md         # Windows-specific quickstart
├── run_demo.sh                   # Linux/macOS demo script
├── run_demo.bat                  # Windows batch demo script
├── run_demo.ps1                  # Windows PowerShell demo script
├── setup_windows.bat             # Windows setup script
├── python/
│   ├── trajectory_generator.py   # Physics-based trajectory generation
│   ├── ml_model.py              # LSTM neural network model
│   ├── data_generator.py        # Training data generation
│   ├── train_model.py           # Model training script
│   ├── simulation.py            # 3D PyQt5 visualization
│   ├── export_to_onnx.py        # ONNX export utility
│   └── utils.py                 # Helper functions
├── cpp/
│   ├── drone_trajectory.h       # C++ header
│   ├── drone_trajectory.cpp     # C++ implementation
│   ├── main.cpp                 # C++ demo application
│   └── CMakeLists.txt           # Cross-platform CMake config
├── models/
│   └── (trained models stored here)
└── data/
    └── (training data stored here)
```

## Platform Support

This project supports the following platforms:

- ✅ **Linux** (Ubuntu 18.04+, Debian, other distros)
- ✅ **Windows 10/11** (with Visual Studio 2017+)
- ✅ **macOS** (10.15+)

### Platform-Specific Documentation

- **Windows Users**: See [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)
- **All Platforms**: See [QUICKSTART.md](QUICKSTART.md)
- **C++ Details**: See [cpp/README_CPP.md](cpp/README_CPP.md)

## License
MIT License
