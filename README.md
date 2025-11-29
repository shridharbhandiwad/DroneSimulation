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
```bash
pip install -r requirements.txt
```

### C++ Setup
```bash
# Install ONNX Runtime
# Ubuntu/Debian:
sudo apt-get install libonnxruntime-dev

# Or build from source:
# https://onnxruntime.ai/docs/build/inferencing.html
```

## Usage

### 1. Generate Training Data
```bash
python data_generator.py
```

### 2. Train the Model
```bash
python train_model.py
```

### 3. Run Simulation
```bash
python simulation.py
```

### 4. Export to ONNX
```bash
python export_to_onnx.py
```

### 5. Build and Run C++ Code
```bash
mkdir build && cd build
cmake ..
make
./drone_trajectory_cpp
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
├── requirements.txt
├── README.md
├── python/
│   ├── trajectory_generator.py
│   ├── ml_model.py
│   ├── data_generator.py
│   ├── train_model.py
│   ├── simulation.py
│   ├── export_to_onnx.py
│   └── utils.py
├── cpp/
│   ├── drone_trajectory.h
│   ├── drone_trajectory.cpp
│   ├── main.cpp
│   └── CMakeLists.txt
├── models/
│   └── (trained models stored here)
└── data/
    └── (training data stored here)
```

## License
MIT License
