# Quick Start: Interactive Waypoint Input

## What You'll Get

This C++ implementation allows you to:
✓ Input waypoints dynamically at runtime  
✓ See ALL intermediate trajectory data points on console  
✓ Use ML model predictions for realistic paths  
✓ Export complete trajectory data to CSV  

## Installation

### 1. Install Build Tools (if not already installed)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y build-essential cmake

# ONNX Runtime is already included in the project
# (at ../onnxruntime-linux-x64-1.17.1/)
```

### 2. Build the Project
```bash
cd /workspace/cpp
mkdir -p build
cd build
cmake ..
make
```

## Running Interactive Mode

### Step 1: Start the Program
```bash
cd /workspace/cpp/build
./drone_trajectory_cpp
```

### Step 2: Choose Interactive Mode
```
=== Select Mode ===
1. Interactive Mode (Dynamic Waypoint Input)  ← Select this
2. Demo Mode (Predefined Waypoints)
3. Benchmark Mode
4. Exit

Enter your choice (1-4): 1
```

### Step 3: Enter Your Waypoints

**Example: Simple rectangular path**
```
How many waypoints do you want to add? 4

Enter waypoint 1 coordinates (x y z): 10 0 5
  Added: (10, 0, 5)

Enter waypoint 2 coordinates (x y z): 10 10 5
  Added: (10, 10, 5)

Enter waypoint 3 coordinates (x y z): 0 10 5
  Added: (0, 10, 5)

Enter waypoint 4 coordinates (x y z): 0 0 5
  Added: (0, 0, 5)
```

### Step 4: Configure Options
```
Enter initial drone position (x y z): 0 0 5

Do you want to save trajectory data to CSV? (y/n): y
Do you want detailed console output for every step? (y/n): y
```

## Example Output

### Detailed Console Output (every step)
```
=== Trajectory Data Points ===
------------------------------------------------------------
Step    0 | t= 0.000s | Pos: (  0.000,   0.000,   5.000) | Vel: ( 0.000,  0.000,  0.000) | Speed:  0.000 m/s | Dist: 10.000 m
Step    1 | t= 0.100s | Pos: (  0.089,   0.012,   5.001) | Vel: ( 0.892,  0.124,  0.015) | Speed:  0.901 m/s | Dist:  9.911 m
Step    2 | t= 0.200s | Pos: (  0.267,   0.048,   5.004) | Vel: ( 1.781,  0.358,  0.031) | Speed:  1.817 m/s | Dist:  9.733 m
Step    3 | t= 0.300s | Pos: (  0.534,   0.107,   5.009) | Vel: ( 2.667,  0.592,  0.048) | Speed:  2.731 m/s | Dist:  9.466 m
...
✓ Reached waypoint 1 at t=2.345s
→ Moving to waypoint 2: (10, 10, 5)
...
✓✓✓ All waypoints reached! ✓✓✓
```

### CSV Output (trajectory_output.csv)
```csv
step,time,pos_x,pos_y,pos_z,vel_x,vel_y,vel_z,acc_x,acc_y,acc_z,speed,distance_to_target,target_x,target_y,target_z
0,0.000,0.000,0.000,5.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000,10.000,10.000,0.000,5.000
1,0.100,0.089,0.012,5.001,0.892,0.124,0.015,8.920,1.240,0.150,0.901,9.911,10.000,0.000,5.000
2,0.200,0.267,0.048,5.004,1.781,0.358,0.031,8.890,2.340,0.160,1.817,9.733,10.000,0.000,5.000
...
```

## Sample Waypoint Patterns

### 1. Simple Square (Ground Level)
```
Waypoints: 4
1: 10 0 5
2: 10 10 5
3: 0 10 5
4: 0 0 5
Initial: 0 0 5
```

### 2. Vertical Climb and Descent
```
Waypoints: 3
1: 0 0 10
2: 10 10 10
3: 10 10 5
Initial: 0 0 5
```

### 3. Zig-Zag Pattern
```
Waypoints: 5
1: 10 5 5
2: 5 -5 7
3: -5 5 9
4: -10 -5 7
5: 0 0 5
Initial: 0 0 5
```

### 4. Circle Approximation (8 points)
```
Waypoints: 8
1: 10 0 5
2: 7.07 7.07 5
3: 0 10 5
4: -7.07 7.07 5
5: -10 0 5
6: -7.07 -7.07 5
7: 0 -10 5
8: 7.07 -7.07 5
Initial: 10 0 5
```

## Understanding the Output

### Position Data
- **Pos (x, y, z)**: Current position in meters
- Format shows 3 decimal places for precision

### Velocity Data  
- **Vel (x, y, z)**: Velocity components in m/s
- **Speed**: Magnitude of velocity vector (total speed)

### Distance
- **Dist**: Euclidean distance to current target waypoint

### Timestamps
- **t**: Time in seconds since simulation start
- Each step = 0.1 seconds (100ms)

## Tips for Best Results

### 1. Waypoint Spacing
- Keep waypoints 5-20 meters apart
- Avoid sudden large jumps (> 30m)
- Gradual altitude changes (< 5m between waypoints)

### 2. Starting Position
- Start near first waypoint for faster convergence
- If starting far away, expect longer initial approach

### 3. Output Options
Choose based on your needs:
- **Detailed output + CSV**: Full analysis and visualization
- **Summary output + CSV**: Quick run with post-processing
- **Detailed output only**: Quick debugging without files
- **Summary only**: Fastest for testing waypoint sequences

### 4. Performance
- Simulation runs 10-100x faster than real-time
- Detailed output slows down due to console I/O
- CSV writing has minimal performance impact

## Using the CSV Data

### Python Visualization
```python
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load data
df = pd.read_csv('trajectory_output.csv')

# 3D plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Plot trajectory
ax.plot(df['pos_x'], df['pos_y'], df['pos_z'], 'b-', label='Trajectory')

# Plot waypoints
waypoints = df.groupby(['target_x', 'target_y', 'target_z']).first()
ax.scatter(waypoints.index.get_level_values(0),
          waypoints.index.get_level_values(1),
          waypoints.index.get_level_values(2),
          c='r', marker='o', s=100, label='Waypoints')

ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Z (m)')
ax.legend()
plt.title('Drone Trajectory')
plt.show()

# Plot speed over time
plt.figure(figsize=(10, 4))
plt.plot(df['time'], df['speed'])
plt.xlabel('Time (s)')
plt.ylabel('Speed (m/s)')
plt.title('Speed Profile')
plt.grid(True)
plt.show()
```

### Excel Analysis
1. Open `trajectory_output.csv` in Excel
2. Create charts for:
   - Position vs Time (line chart)
   - Speed vs Time (area chart)
   - Distance to Target vs Time (line chart)
3. Use pivot tables to analyze waypoint segments

## Troubleshooting

### "ML model files not found"
**Solution**: The program will use physics-based prediction automatically.  
**Optional**: Train ML model for better predictions:
```bash
cd /workspace/python
python data_generator.py
python train_model.py
python export_to_onnx.py
```

### "Invalid input"
**Problem**: Wrong format for coordinates  
**Solution**: Enter exactly 3 numbers separated by spaces
```
✗ Wrong: (10, 20, 5)
✗ Wrong: 10,20,5
✓ Correct: 10 20 5
```

### Program hangs
**Problem**: Waiting for user input  
**Solution**: Check if you need to answer a y/n question

### Trajectory doesn't reach waypoints
**Problem**: Waypoints too far or simulation timeout  
**Solutions**:
- Reduce distance between waypoints
- Increase max_steps in code (default: 1000)
- Check initial position is reasonable

## Advanced: File Input Mode

To add file-based waypoint input, modify `main.cpp`:

```cpp
// Add this function after getDynamicWaypoints()
std::vector<Vec3> loadWaypointsFromFile(const std::string& filename) {
    std::vector<Vec3> waypoints;
    std::ifstream file(filename);
    
    if (!file.is_open()) {
        std::cerr << "Could not open file: " << filename << std::endl;
        return waypoints;
    }
    
    std::string line;
    while (std::getline(file, line)) {
        // Skip comments and empty lines
        if (line.empty() || line[0] == '#') continue;
        
        std::istringstream iss(line);
        float x, y, z;
        if (iss >> x >> y >> z) {
            waypoints.push_back(Vec3(x, y, z));
        }
    }
    
    return waypoints;
}

// Then in runInteractiveTrajectory(), add option:
bool use_file = askYesNo("Load waypoints from file?");
if (use_file) {
    waypoints = loadWaypointsFromFile("../example_waypoints.txt");
} else {
    waypoints = getDynamicWaypoints();
}
```

## Next Steps

1. **Try different patterns**: Test various waypoint configurations
2. **Analyze trajectories**: Use CSV output for detailed analysis
3. **Visualize results**: Plot trajectories in Python/MATLAB
4. **Train ML model**: For more realistic predictions
5. **Integrate with simulator**: Connect to drone simulation software

## Support

For more information, see:
- `README_INTERACTIVE_MODE.md` - Detailed technical documentation
- `drone_trajectory.h` - API reference
- `../python/` - ML model training pipeline
