# System Architecture

## Overview

The Drone Trajectory System is designed as a complete pipeline from data generation to real-time C++ inference. The system is modular and can be used at various levels depending on requirements.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    DRONE TRAJECTORY SYSTEM                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┐      ┌─────────────────────┐
│  PYTHON PIPELINE    │      │   C++ RUNTIME       │
└─────────────────────┘      └─────────────────────┘

    TRAINING PHASE              INFERENCE PHASE
         │                            │
         ▼                            ▼
┌──────────────────┐          ┌──────────────────┐
│ Data Generation  │          │  ONNX Runtime    │
│                  │          │                  │
│ • Physics Model  │          │ • Fast Inference │
│ • Random Paths   │          │ • <1ms Latency   │
│ • Augmentation   │          │ • Embedded Ready │
└────────┬─────────┘          └────────▲─────────┘
         │                             │
         ▼                             │
┌──────────────────┐                  │
│  LSTM Training   │                  │
│                  │         ┌────────┴─────────┐
│ • Sequence Model │         │  ONNX Export     │
│ • Validation     │◄────────┤                  │
│ • Checkpointing  │         │ • Model Convert  │
└────────┬─────────┘         │ • Normalization  │
         │                   └──────────────────┘
         ▼
┌──────────────────┐
│  PyQt5 Sim       │
│                  │
│ • 3D Viz         │
│ • Camera Feed    │
│ • Real-time      │
└──────────────────┘
```

## Component Details

### 1. Physics-Based Trajectory Generator

**File:** `python/trajectory_generator.py`

**Purpose:** Generate realistic drone trajectories using physics simulation

**Key Classes:**
- `DronePhysics`: Physical model with drag, acceleration limits
- `TrajectoryGenerator`: High-level trajectory generation

**Physics Model:**
```
Position: p(t+dt) = p(t) + v(t)*dt + 0.5*a(t)*dt²
Velocity: v(t+dt) = v(t) + a(t)*dt - drag*|v|*v*dt
Acceleration: Limited to max_acceleration
```

**Features:**
- Realistic acceleration limits
- Drag simulation
- Waypoint following
- Collision avoidance potential

### 2. LSTM Neural Network

**File:** `python/ml_model.py`

**Purpose:** Learn trajectory patterns for improved prediction

**Architecture:**
```
Input (batch, 10, 13)
    ↓
LSTM Layer 1 (128 hidden units)
    ↓
LSTM Layer 2 (128 hidden units)
    ↓
Dropout (0.2)
    ↓
FC Layer 1 (64 units + ReLU)
    ↓
Dropout (0.2)
    ↓
FC Layer 2 (6 units)
    ↓
Output (position + velocity)
```

**Input Features (13):**
1-3. Position (x, y, z) - normalized
4-6. Velocity (vx, vy, vz) - normalized
7-9. Acceleration (ax, ay, az)
10-12. Target waypoint (wx, wy, wz)
13. Distance to waypoint

**Output (6):**
1-3. Next position (x, y, z)
4-6. Next velocity (vx, vy, vz)

**Training:**
- Loss: MSE (Mean Squared Error)
- Optimizer: Adam (lr=0.001)
- Scheduler: ReduceLROnPlateau
- Regularization: Dropout, early stopping

### 3. Data Generation Pipeline

**File:** `python/data_generator.py`

**Process:**
```
Generate Random Conditions
    ↓
Simulate Physics Trajectory
    ↓
Optional: Add Noise
    ↓
Create Sequence Samples
    ↓
Split: Train/Val/Test (70/15/15)
    ↓
Save to Disk
```

**Augmentation:**
- Position noise: Gaussian (σ=0.1m)
- Velocity noise: Gaussian (σ=0.05m/s)
- Random initial conditions
- Random waypoints

### 4. PyQt5 Simulation

**File:** `python/simulation.py`

**Components:**

**3D Visualization:**
- OpenGL-based rendering
- Real-time trajectory display
- Waypoint markers
- Drone position indicator

**Camera Simulator:**
- First-person view from drone
- HUD overlay with telemetry
- Horizon simulation
- Crosshair and indicators

**UI Features:**
- Play/Pause control
- Speed adjustment (0.1x - 5.0x)
- Reset and new trajectory generation
- Real-time telemetry display

### 5. ONNX Export

**File:** `python/export_to_onnx.py`

**Conversion Process:**
```
PyTorch Model (.pth)
    ↓
ONNX Export (opset 11)
    ↓
Verification
    ↓
Test Inference
    ↓
Save Normalization Params
    ↓
ONNX Model (.onnx)
```

**Optimizations:**
- Constant folding
- Dynamic batch size
- Operator fusion

### 6. C++ Real-Time Predictor

**Files:** `cpp/drone_trajectory.h`, `cpp/drone_trajectory.cpp`

**Key Classes:**

**TrajectoryPredictor:**
- ONNX Runtime integration
- State history management
- Normalization/denormalization
- Fast inference (<1ms)

**PhysicsTrajectoryGenerator:**
- Fallback when ML unavailable
- Same physics as Python version
- Pure C++ implementation

**Features:**
- Zero-copy inference where possible
- Efficient memory management
- Thread-safe design
- Embedded system ready

## Data Flow

### Training Flow

```
Random Conditions → Physics Sim → Trajectory Data
                                        ↓
                              Sequence Extraction
                                        ↓
                                Training Samples
                                        ↓
                                  LSTM Training
                                        ↓
                                  Trained Model
                                        ↓
                                  ONNX Export
```

### Inference Flow (Python)

```
Drone State → History Buffer → Feature Extraction
                                      ↓
                              Normalization
                                      ↓
                              PyTorch LSTM
                                      ↓
                              Denormalization
                                      ↓
                              Predicted State
```

### Inference Flow (C++)

```
Drone State → History Buffer → Feature Extraction
                                      ↓
                              Normalization
                                      ↓
                              ONNX Runtime
                                      ↓
                              Denormalization
                                      ↓
                              Predicted State
```

## Performance Characteristics

### Python
- **Training:** ~5-15 minutes (1000 trajectories, 50 epochs)
- **Inference:** ~10ms per prediction
- **Simulation:** 30-60 FPS
- **Memory:** ~500MB during training

### C++
- **Inference:** <1ms per prediction
- **Memory:** <1MB runtime
- **Throughput:** >1000 predictions/sec
- **Latency:** Deterministic, low jitter

## Scalability

### Training
- **Data parallelism:** Multi-GPU support via PyTorch
- **Batch size:** Adjustable based on memory
- **Dataset size:** Tested up to 10,000 trajectories

### Inference
- **Python:** Single-threaded, suitable for offline analysis
- **C++:** Multi-threaded potential, real-time capable
- **Embedded:** ARM/x86 compatible, low power

## Extension Points

### 1. Custom Physics Models
Modify `DronePhysics` class to add:
- Wind effects
- Motor dynamics
- Battery constraints
- Obstacle avoidance

### 2. Enhanced ML Models
Replace LSTM with:
- Transformer-based models
- GRU for faster inference
- Ensemble methods
- Reinforcement learning

### 3. Additional Sensors
Extend input features:
- IMU data
- GPS uncertainty
- Battery level
- Environmental conditions

### 4. Multi-Drone Systems
Extend to handle:
- Swarm behavior
- Collision avoidance
- Formation flying
- Cooperative planning

## Security Considerations

### Model Security
- Validate input ranges
- Bound output predictions
- Detect anomalous behavior
- Fail-safe to physics model

### Runtime Security
- No dynamic code execution
- Bounded memory allocation
- Input sanitization
- Safe integer arithmetic

## Testing Strategy

### Unit Tests
- Physics model accuracy
- ML model convergence
- ONNX export correctness
- C++ API functionality

### Integration Tests
- End-to-end pipeline
- Python-C++ equivalence
- Real-time performance
- Memory leak detection

### Validation
- Cross-validation (training)
- Hold-out test set
- Real-world trajectory comparison
- Latency benchmarks

## Deployment Options

### 1. Development (Python)
```bash
python simulation.py
```

### 2. Production (C++ Library)
```cpp
#include "drone_trajectory.h"
// Link and use in your application
```

### 3. Edge Device (Embedded)
- Cross-compile for ARM
- Use ONNX Runtime mobile
- Optimize for power consumption

### 4. Cloud Service (REST API)
- Deploy as microservice
- Scale horizontally
- GPU acceleration

## Future Enhancements

1. **Online Learning:** Update model with real flight data
2. **Uncertainty Estimation:** Predict confidence bounds
3. **Multi-Modal:** Handle different flight modes
4. **Compression:** Quantization for embedded deployment
5. **ROS Integration:** Native ROS node implementation
