#!/bin/bash
# Test script for interactive waypoint simulation
# This demonstrates the new dynamic waypoint input feature

echo "====================================="
echo "Interactive Waypoint Test Script"
echo "====================================="
echo ""

# Check if build exists
if [ ! -f "build/drone_trajectory_cpp" ]; then
    echo "Building the project..."
    mkdir -p build
    cd build
    cmake ..
    make
    cd ..
    echo ""
fi

# Check if executable exists
if [ ! -f "build/drone_trajectory_cpp" ]; then
    echo "Error: Build failed or executable not found"
    echo "Please build the project manually:"
    echo "  cd /workspace/cpp"
    echo "  mkdir -p build && cd build"
    echo "  cmake .. && make"
    exit 1
fi

echo "Executable found: build/drone_trajectory_cpp"
echo ""

# Create test waypoint file
echo "Creating test waypoint file..."
cat > test_waypoints.txt << EOF
# Test waypoints - simple square pattern
10 0 5
10 10 5
0 10 5
0 0 5
EOF

echo "Test waypoints created in test_waypoints.txt:"
cat test_waypoints.txt | grep -v "^#"
echo ""

# Prepare automated input for testing
# This simulates user input: mode 1 (interactive), 4 waypoints, etc.
TEST_INPUT="1
4
10 0 5
10 10 5
0 10 5
0 0 5
0 0 5
y
n
"

echo "====================================="
echo "Running Interactive Simulation Test"
echo "====================================="
echo ""
echo "Input configuration:"
echo "  - Mode: 1 (Interactive)"
echo "  - Waypoints: 4 (square pattern)"
echo "  - Initial position: (0, 0, 5)"
echo "  - CSV export: Yes"
echo "  - Detailed output: No (summary mode)"
echo ""
echo "Starting simulation..."
echo ""

# Run the program with test input
echo "$TEST_INPUT" | ./build/drone_trajectory_cpp

echo ""
echo "====================================="
echo "Test Complete"
echo "====================================="
echo ""

# Check if CSV was created
if [ -f "trajectory_output.csv" ]; then
    echo "✓ CSV file created successfully"
    LINE_COUNT=$(wc -l < trajectory_output.csv)
    echo "  - Lines in CSV: $LINE_COUNT"
    echo "  - First 5 lines:"
    head -5 trajectory_output.csv
    echo "  ..."
    echo ""
    echo "To view the full trajectory data:"
    echo "  cat trajectory_output.csv"
    echo ""
    echo "To visualize (if you have Python with pandas/matplotlib):"
    echo "  python3 << 'PYEOF'
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('trajectory_output.csv')
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Position
axes[0,0].plot(df['time'], df['pos_x'], label='X')
axes[0,0].plot(df['time'], df['pos_y'], label='Y')
axes[0,0].plot(df['time'], df['pos_z'], label='Z')
axes[0,0].set_xlabel('Time (s)')
axes[0,0].set_ylabel('Position (m)')
axes[0,0].legend()
axes[0,0].set_title('Position vs Time')
axes[0,0].grid(True)

# Speed
axes[0,1].plot(df['time'], df['speed'])
axes[0,1].set_xlabel('Time (s)')
axes[0,1].set_ylabel('Speed (m/s)')
axes[0,1].set_title('Speed vs Time')
axes[0,1].grid(True)

# Distance to target
axes[1,0].plot(df['time'], df['distance_to_target'])
axes[1,0].set_xlabel('Time (s)')
axes[1,0].set_ylabel('Distance (m)')
axes[1,0].set_title('Distance to Target')
axes[1,0].grid(True)

# 2D trajectory (top view)
axes[1,1].plot(df['pos_x'], df['pos_y'], 'b-', alpha=0.5)
axes[1,1].scatter(df['target_x'].unique(), df['target_y'].unique(), 
                 c='red', s=100, marker='o', label='Waypoints')
axes[1,1].set_xlabel('X (m)')
axes[1,1].set_ylabel('Y (m)')
axes[1,1].set_title('Trajectory (Top View)')
axes[1,1].legend()
axes[1,1].grid(True)
axes[1,1].axis('equal')

plt.tight_layout()
plt.savefig('trajectory_analysis.png', dpi=150)
print('Saved to trajectory_analysis.png')
plt.show()
PYEOF"
else
    echo "⚠ Warning: CSV file not created"
    echo "  This is normal if:"
    echo "  - Build failed"
    echo "  - User declined CSV export"
    echo "  - Program encountered an error"
fi

echo ""
echo "To run the interactive mode manually:"
echo "  cd /workspace/cpp"
echo "  ./build/drone_trajectory_cpp"
echo "  Select option 1 (Interactive Mode)"
echo ""
