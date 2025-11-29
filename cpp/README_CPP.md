# C++ Drone Trajectory Predictor

## Overview

This C++ implementation provides real-time drone trajectory prediction using the trained ONNX model.

## Dependencies

1. **ONNX Runtime** (Required for ML inference)
2. **CMake** (3.15 or higher)
3. **C++17 compatible compiler**

## Installation

### Ubuntu/Debian

```bash
# Install ONNX Runtime
wget https://github.com/microsoft/onnxruntime/releases/download/v1.16.0/onnxruntime-linux-x64-1.16.0.tgz
tar -xzf onnxruntime-linux-x64-1.16.0.tgz
sudo cp -r onnxruntime-linux-x64-1.16.0/include/* /usr/local/include/
sudo cp -r onnxruntime-linux-x64-1.16.0/lib/* /usr/local/lib/
sudo ldconfig
```

### macOS

```bash
# Install using Homebrew
brew install onnxruntime
```

### Windows

Download ONNX Runtime from:
https://github.com/microsoft/onnxruntime/releases

Extract and set `ONNXRUNTIME_DIR` environment variable.

## Building

```bash
cd cpp
mkdir build
cd build
cmake ..
make
```

If ONNX Runtime is in a custom location:

```bash
cmake -DONNXRUNTIME_DIR=/path/to/onnxruntime ..
make
```

## Usage

### Basic Usage

```bash
./drone_trajectory_cpp
```

This will run:
1. ML-based trajectory prediction (if model is available)
2. Performance benchmark
3. Physics-based trajectory (as fallback/comparison)

### As a Library

Include the header in your C++ project:

```cpp
#include "drone_trajectory.h"

using namespace drone;

// Create predictor
TrajectoryPredictor predictor(
    "path/to/drone_trajectory.onnx",
    "path/to/drone_trajectory_normalization.txt",
    10  // sequence length
);

// Initialize
if (!predictor.initialize()) {
    // Handle error
}

// Add states to history
DroneState state;
state.position = Vec3(0, 0, 5);
state.velocity = Vec3(0, 0, 0);
state.acceleration = Vec3(0, 0, 0);
predictor.addState(state);

// Predict next state
Vec3 target_waypoint(10, 10, 8);
DroneState predicted;
if (predictor.predict(target_waypoint, predicted)) {
    // Use predicted state
    std::cout << "Predicted position: " 
              << predicted.position.x << ", "
              << predicted.position.y << ", "
              << predicted.position.z << std::endl;
}
```

### Physics-Only Mode

If you don't have the ML model, use the physics-based generator:

```cpp
#include "drone_trajectory.h"

using namespace drone;

PhysicsTrajectoryGenerator physics;

DroneState current, next;
current.position = Vec3(0, 0, 5);
current.velocity = Vec3(0, 0, 0);

Vec3 target(10, 10, 8);
physics.update(current, target, 0.1f, next);
```

## API Reference

### TrajectoryPredictor

**Constructor:**
```cpp
TrajectoryPredictor(
    const std::string& model_path,
    const std::string& normalization_path,
    int sequence_length = 10
);
```

**Methods:**
- `bool initialize()` - Initialize the predictor
- `void addState(const DroneState& state)` - Add state to history
- `bool predict(const Vec3& target, DroneState& predicted)` - Predict next state
- `void reset()` - Clear history
- `bool isReady()` - Check if enough history for prediction

### PhysicsTrajectoryGenerator

**Constructor:**
```cpp
PhysicsTrajectoryGenerator(
    float max_speed = 15.0f,
    float max_acceleration = 5.0f,
    float max_vertical_speed = 5.0f
);
```

**Methods:**
- `void update(const DroneState& current, const Vec3& target, float dt, DroneState& next)` - Update state

### Data Structures

**Vec3:**
```cpp
struct Vec3 {
    float x, y, z;
    float norm() const;
    Vec3 normalized() const;
    // Operators: +, -, *
};
```

**DroneState:**
```cpp
struct DroneState {
    Vec3 position;
    Vec3 velocity;
    Vec3 acceleration;
    double timestamp;
};
```

## Performance

On a typical modern CPU:
- **Inference time:** < 1ms per prediction
- **Frequency:** > 1000 Hz
- **Real-time capable:** Yes (easily meets 10Hz requirement for 100ms updates)

## Troubleshooting

### ONNX Runtime not found

If CMake cannot find ONNX Runtime:

```bash
cmake -DONNXRUNTIME_DIR=/path/to/onnxruntime ..
```

Or set environment variable:

```bash
export ONNXRUNTIME_DIR=/path/to/onnxruntime
```

### Model files not found

Make sure to run the Python pipeline first:

```bash
cd ../python
python data_generator.py
python train_model.py
python export_to_onnx.py
```

### Runtime library not found

On Linux:

```bash
export LD_LIBRARY_PATH=/path/to/onnxruntime/lib:$LD_LIBRARY_PATH
```

Or add to `/etc/ld.so.conf.d/` and run `sudo ldconfig`.

## Integration Examples

### ROS Integration

```cpp
#include "drone_trajectory.h"
#include <ros/ros.h>
#include <geometry_msgs/PoseStamped.h>

class DroneTrajectoryNode {
private:
    drone::TrajectoryPredictor predictor;
    ros::Subscriber pose_sub;
    ros::Publisher pred_pub;
    
public:
    DroneTrajectoryNode() 
        : predictor("model.onnx", "normalization.txt", 10) {
        
        predictor.initialize();
        
        pose_sub = nh.subscribe("drone/pose", 10, 
            &DroneTrajectoryNode::poseCallback, this);
        pred_pub = nh.advertise<geometry_msgs::PoseStamped>(
            "drone/predicted_pose", 10);
    }
    
    void poseCallback(const geometry_msgs::PoseStamped& msg) {
        // Convert to DroneState and predict...
    }
};
```

### Embedded Systems

The C++ code is designed to work on embedded systems:

- No dynamic memory allocation in prediction loop
- Small memory footprint (< 1MB)
- Fast inference (< 1ms)
- No external dependencies except ONNX Runtime

## License

MIT License
