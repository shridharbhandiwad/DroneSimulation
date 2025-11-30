# Interactive Waypoint Mode - C++ Implementation

## Overview

This implementation provides a dynamic waypoint input system in C++ that allows users to:
- Enter waypoints interactively at runtime
- View all intermediate trajectory data points on the console
- Export trajectory data to CSV for analysis
- Use ML model predictions for realistic trajectory generation

## Features

### 1. Dynamic Waypoint Input
- Interactive command-line interface for waypoint entry
- Supports any number of waypoints (1-100)
- Real-time validation of user input
- Easy-to-use format: `x y z` coordinates

### 2. Detailed Console Output
Users can choose between two output modes:

**Summary Mode** (default):
- Prints status every 10 steps (1 second of simulation time)
- Shows progress through waypoints
- Displays distance to target

**Detailed Mode**:
- Prints every single data point
- Shows complete state information:
  - Position (x, y, z)
  - Velocity (x, y, z)
  - Speed
  - Distance to target
  - Timestamp

### 3. CSV Data Export
- Optional CSV file export of all trajectory data
- Includes: position, velocity, acceleration, speed, distance, target
- Perfect for post-processing and visualization
- File: `trajectory_output.csv`

### 4. Model Integration
- Automatically uses ML model if available
- Falls back to physics-based prediction if model not found
- Seamless switching between prediction methods

## Building and Running

### Prerequisites
```bash
# Install dependencies
sudo apt-get install cmake build-essential

# For ONNX Runtime (Linux)
# The onnxruntime library should be in ../onnxruntime-linux-x64-1.17.1/
```

### Build Instructions
```bash
cd cpp
mkdir -p build
cd build
cmake ..
make
```

### Running the Program
```bash
# Run from the build directory
./drone_trajectory_cpp

# Or from the cpp directory
cd cpp/build && ./drone_trajectory_cpp
```

## Usage Guide

### Interactive Mode (Mode 1)

1. **Start the program**:
   ```
   ./drone_trajectory_cpp
   ```

2. **Select Interactive Mode**:
   ```
   === Select Mode ===
   1. Interactive Mode (Dynamic Waypoint Input)
   2. Demo Mode (Predefined Waypoints)
   3. Benchmark Mode
   4. Exit
   
   Enter your choice (1-4): 1
   ```

3. **Enter number of waypoints**:
   ```
   === Dynamic Waypoint Input ===
   How many waypoints do you want to add? 3
   ```

4. **Enter each waypoint**:
   ```
   Enter waypoints in format: x y z (separated by spaces)
   Example: 10.5 20.0 8.5

   Enter waypoint 1 coordinates (x y z): 10 10 5
     Added: (10, 10, 5)

   Enter waypoint 2 coordinates (x y z): 20 5 8
     Added: (20, 5, 8)

   Enter waypoint 3 coordinates (x y z): 0 0 5
     Added: (0, 0, 5)
   ```

5. **Set initial position**:
   ```
   Enter initial drone position (x y z): 0 0 5
   ```

6. **Configure output options**:
   ```
   Do you want to save trajectory data to CSV? (y/n): y
   Do you want detailed console output for every step? (y/n): y
   ```

7. **Watch the simulation**:
   ```
   === Starting Simulation ===
   Initial State:
     Position: (0.00, 0.00, 5.00)
     Velocity: (0.00, 0.00, 0.00)
     Time: 0.00s

   Using ML-based trajectory prediction

   === Trajectory Data Points ===
   --------------------------------------------------------
   Step    0 | t= 0.000s | Pos: (  0.000,   0.000,   5.000) | Vel: ( 0.000,  0.000,  0.000) | Speed:  0.000 m/s | Dist: 11.180 m
   Step    1 | t= 0.100s | Pos: (  0.125,   0.125,   5.015) | Vel: ( 1.250,  1.250,  0.150) | Speed:  1.784 m/s | Dist: 11.034 m
   ...
   ```

### Example Session

```
╔═══════════════════════════════════════════════╗
║  Drone Trajectory Prediction - C++ Demo     ║
║  Dynamic Waypoint Input with Model Output   ║
╚═══════════════════════════════════════════════╝

✓ ML model loaded successfully!

=== Dynamic Waypoint Input ===
How many waypoints do you want to add? 4

Enter waypoint 1 coordinates (x y z): 10 10 8
  Added: (10, 10, 8)

Enter waypoint 2 coordinates (x y z): 20 5 10
  Added: (20, 5, 10)

Enter waypoint 3 coordinates (x y z): 15 -10 7
  Added: (15, -10, 7)

Enter waypoint 4 coordinates (x y z): 0 0 5
  Added: (0, 0, 5)

=== Waypoint List ===
  Waypoint 1: (10.00, 10.00, 8.00)
  Waypoint 2: (20.00, 5.00, 10.00)
  Waypoint 3: (15.00, -10.00, 7.00)
  Waypoint 4: (0.00, 0.00, 5.00)
=====================

Enter initial drone position (x y z): 0 0 5

Do you want to save trajectory data to CSV? (y/n): y
Do you want detailed console output for every step? (y/n): n

=== Starting Simulation ===
Initial State:
  Position: (0.00, 0.00, 5.00)
  Velocity: (0.00, 0.00, 0.00)
  Time: 0.00s

Using ML-based trajectory prediction

Step 0 | t=0.00s | Distance: 11.18m | Waypoint 1/4
Step 10 | t=1.00s | Distance: 5.23m | Waypoint 1/4

✓ Reached waypoint 1 at t=2.34s
→ Moving to waypoint 2: (20, 5, 10)

Step 30 | t=3.00s | Distance: 8.45m | Waypoint 2/4

✓ Reached waypoint 2 at t=5.67s
→ Moving to waypoint 3: (15, -10, 7)

✓ Reached waypoint 3 at t=8.91s
→ Moving to waypoint 4: (0, 0, 5)

✓ Reached waypoint 4 at t=12.34s

✓✓✓ All waypoints reached! ✓✓✓

=== Simulation Complete ===
Total steps: 124
Total time: 12.4 seconds
Waypoints reached: 4/4

Final State:
  Position: (0.12, 0.05, 5.01)
  Velocity: (0.23, 0.11, 0.05)
  Time: 12.40s

Trajectory data saved to: trajectory_output.csv

✓ Demo complete!
```

## Output Data Format

### Console Output (Detailed Mode)

Each line contains:
- Step number
- Timestamp (seconds)
- Position (x, y, z) in meters
- Velocity (x, y, z) in m/s
- Speed (magnitude) in m/s
- Distance to current target in meters

### CSV Output Format

The CSV file contains the following columns:
```
step,time,pos_x,pos_y,pos_z,vel_x,vel_y,vel_z,acc_x,acc_y,acc_z,speed,distance_to_target,target_x,target_y,target_z
```

Example row:
```csv
0,0.000,0.000,0.000,5.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000,14.142,10.000,10.000,8.000
1,0.100,0.125,0.125,5.015,1.250,1.250,0.150,12.500,12.500,1.500,1.784,13.982,10.000,10.000,8.000
```

## Code Structure

### Key Functions

#### `getDynamicWaypoints()`
- Prompts user for waypoint count
- Reads waypoint coordinates interactively
- Validates input and provides feedback
- Returns vector of Vec3 waypoints

#### `runInteractiveTrajectory(TrajectoryPredictor* predictor)`
- Main interactive simulation loop
- Handles waypoint input
- Manages ML/physics prediction
- Prints trajectory data points
- Exports to CSV

#### `printDetailedState()`
- Formats and displays complete state information
- Shows position, velocity, speed, and distance
- Provides timestamp and step number

#### `TrajectoryLogger` class
- Handles CSV file creation and writing
- Automatically writes header
- Logs each trajectory state
- Closes file on destruction

### Integration with ML Model

The implementation seamlessly integrates with the ONNX model:

```cpp
// Initialize predictor
TrajectoryPredictor predictor(model_path, norm_path, 10);
predictor.initialize();

// Build initial history (required for LSTM)
for (int i = 0; i < predictor.getSequenceLength(); ++i) {
    predictor.addState(current_state);
    // ... update state
}

// Prediction loop
DroneState predicted_state;
if (predictor.predict(target_waypoint, predicted_state)) {
    current_state = predicted_state;
    predictor.addState(current_state);
    // ... print and log state
}
```

## Tips and Best Practices

### Waypoint Selection
- Start with waypoints that are not too far apart (< 20m)
- Keep altitude changes moderate (< 5m between waypoints)
- The drone requires ~0.5m accuracy to consider a waypoint "reached"

### Output Options
- Use **summary mode** for quick testing (faster, cleaner)
- Use **detailed mode** for debugging and analysis
- Always enable CSV export for post-processing

### Performance
- The ML model runs at 100-500 Hz on modern CPUs
- Simulation runs in real-time (100ms per step)
- Can simulate 30 seconds in under 1 second

### Coordinate System
- X: forward/backward
- Y: left/right  
- Z: up/down (altitude)
- Units: meters
- Origin: (0, 0, 0)

## Troubleshooting

### Model Not Found
```
⚠ Warning: ML model files not found.
```
**Solution**: Train the model first:
```bash
cd python
python data_generator.py
python train_model.py
python export_to_onnx.py
```

### Input Validation Errors
```
Invalid input! Please enter three numbers (x y z):
```
**Solution**: Ensure you enter three space-separated numbers, e.g., `10.5 20.0 8.5`

### CSV File Not Created
**Solution**: Check write permissions in the current directory

## Advanced Usage

### Programmatic Waypoint Input

You can also modify the code to read waypoints from a file:

```cpp
std::vector<Vec3> loadWaypointsFromFile(const std::string& filename) {
    std::vector<Vec3> waypoints;
    std::ifstream file(filename);
    
    float x, y, z;
    while (file >> x >> y >> z) {
        waypoints.push_back(Vec3(x, y, z));
    }
    
    return waypoints;
}
```

### Real-time Visualization

You can pipe the CSV output to Python for real-time visualization:

```bash
./drone_trajectory_cpp | python ../python/visualize_trajectory.py
```

## See Also

- `drone_trajectory.h` - Class definitions
- `drone_trajectory.cpp` - Implementation details
- `CMakeLists.txt` - Build configuration
- `../python/` - Python training pipeline
