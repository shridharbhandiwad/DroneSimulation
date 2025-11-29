# Quick Start Guide

## Complete Workflow from Zero to Running Demo

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Generate Training Data

```bash
cd python
python data_generator.py
```

This will create:
- `../data/train_data.pkl` (training dataset)
- `../data/val_data.pkl` (validation dataset)
- `../data/test_data.pkl` (test dataset)
- `../data/normalization.pkl` (normalization parameters)

Expected time: 2-5 minutes for 1000 trajectories

### Step 3: Train the LSTM Model

```bash
python train_model.py
```

This will create:
- `../models/best_model.pth` (best model based on validation loss)
- `../models/final_model.pth` (final model after all epochs)
- `../models/training_curves.png` (training visualization)

Expected time: 5-15 minutes depending on GPU availability

### Step 4: Run Python Simulation

```bash
python simulation.py
```

This opens a PyQt5 window with:
- 3D trajectory visualization
- Real-time drone camera feed
- Telemetry data
- Playback controls

### Step 5: Export to ONNX for C++

```bash
python export_to_onnx.py
```

This creates:
- `../models/drone_trajectory.onnx` (ONNX model)
- `../models/drone_trajectory_normalization.txt` (normalization params)

### Step 6: Build C++ Code

```bash
cd ../cpp
mkdir build
cd build
cmake ..
make
```

### Step 7: Run C++ Demo

```bash
./drone_trajectory_cpp
```

This runs:
1. ML-based trajectory prediction
2. Performance benchmark
3. Physics-based trajectory (comparison)

## Troubleshooting

### Python Issues

**Problem:** PyQt5 not displaying window

**Solution:**
```bash
# Linux
sudo apt-get install python3-pyqt5
# macOS
brew install pyqt5
```

**Problem:** CUDA out of memory

**Solution:** Edit `train_model.py` and reduce batch size:
```python
train_model(batch_size=32)  # default is 64
```

### C++ Issues

**Problem:** ONNX Runtime not found

**Solution:**
```bash
# Ubuntu/Debian
wget https://github.com/microsoft/onnxruntime/releases/download/v1.16.0/onnxruntime-linux-x64-1.16.0.tgz
tar -xzf onnxruntime-linux-x64-1.16.0.tgz
sudo cp -r onnxruntime-linux-x64-1.16.0/include/* /usr/local/include/
sudo cp -r onnxruntime-linux-x64-1.16.0/lib/* /usr/local/lib/
sudo ldconfig
```

**Problem:** Model files not found

**Solution:** Make sure you completed steps 2-5 to generate and export the model

## Quick Test Without Training

If you want to test without training (physics-only mode):

```bash
cd python
python simulation.py  # Will use physics-based trajectory only
```

```bash
cd cpp/build
./drone_trajectory_cpp  # Will run physics-based trajectory
```

## System Requirements

### Minimum:
- Python 3.8+
- 4GB RAM
- 1GB disk space

### Recommended:
- Python 3.10+
- 8GB RAM
- NVIDIA GPU with CUDA support
- 2GB disk space

## What Each Component Does

### Python Components

1. **trajectory_generator.py**: Physics-based trajectory generation using drone dynamics
2. **ml_model.py**: LSTM neural network for learning trajectory patterns
3. **data_generator.py**: Creates training data from simulated trajectories
4. **train_model.py**: Trains the LSTM model
5. **simulation.py**: Interactive 3D visualization with camera feed
6. **export_to_onnx.py**: Converts PyTorch model to ONNX format

### C++ Components

1. **drone_trajectory.h/cpp**: Core prediction engine with ONNX Runtime
2. **main.cpp**: Demo application showing ML and physics-based prediction
3. **CMakeLists.txt**: Build configuration

## Next Steps

After completing the quickstart:

1. **Experiment with different waypoints** in `simulation.py`
2. **Tune model parameters** in `ml_model.py`
3. **Generate more training data** by increasing `num_trajectories` in `data_generator.py`
4. **Integrate into your project** using the C++ or Python API
5. **Deploy on embedded systems** using the C++ implementation

## Performance Expectations

- **Python simulation:** 30-60 FPS
- **ML inference (Python):** ~10ms per prediction
- **ML inference (C++):** <1ms per prediction
- **Real-time capable:** Yes, both Python and C++ can run at 10Hz (100ms interval)

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review the code comments for implementation details
3. See cpp/README_CPP.md for C++ specific information
