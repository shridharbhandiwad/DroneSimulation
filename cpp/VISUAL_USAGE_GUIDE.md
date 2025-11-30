# 🎨 Visual Usage Guide - Interactive Waypoint System

## 📺 What You'll See

This guide shows exactly what happens when you run the interactive waypoint system.

---

## 🚀 Step-by-Step Visual Walkthrough

### Step 1: Launch the Program

**Command:**
```bash
cd /workspace/cpp/build
./drone_trajectory_cpp
```

**You'll See:**
```
╔═══════════════════════════════════════════════╗
║  Drone Trajectory Prediction - C++ Demo     ║
║  Dynamic Waypoint Input with Model Output   ║
╚═══════════════════════════════════════════════╝

✓ ML model loaded successfully!

=== Select Mode ===
1. Interactive Mode (Dynamic Waypoint Input)  ← Choose this!
2. Demo Mode (Predefined Waypoints)
3. Benchmark Mode
4. Exit

Enter your choice (1-4): _
```

---

### Step 2: Enter Number of Waypoints

**You Type:** `1`

**You'll See:**
```
=== Dynamic Waypoint Input ===
How many waypoints do you want to add? _
```

**You Type:** `3`

**You'll See:**
```
Enter waypoints in format: x y z (separated by spaces)
Example: 10.5 20.0 8.5

Enter waypoint 1 coordinates (x y z): _
```

---

### Step 3: Enter Each Waypoint

**You Type:** `10 10 5`

**You'll See:**
```
  Added: (10, 10, 5)

Enter waypoint 2 coordinates (x y z): _
```

**You Type:** `20 5 8`

**You'll See:**
```
  Added: (20, 5, 8)

Enter waypoint 3 coordinates (x y z): _
```

**You Type:** `0 0 5`

**You'll See:**
```
  Added: (0, 0, 5)

=== Waypoint List ===
  Waypoint 1: (10.00, 10.00, 5.00)
  Waypoint 2: (20.00, 5.00, 8.00)
  Waypoint 3: (0.00, 0.00, 5.00)
=====================

Enter initial drone position (x y z): _
```

---

### Step 4: Set Initial Position

**You Type:** `0 0 5`

**You'll See:**
```
Do you want to save trajectory data to CSV? (y/n): _
```

---

### Step 5: Configure Options

**You Type:** `y`

**You'll See:**
```
Do you want detailed console output for every step? (y/n): _
```

**You Type:** `y` (for detailed) or `n` (for summary)

---

### Step 6A: Detailed Output Mode (if you chose 'y')

**You'll See:**
```
=== Starting Simulation ===
Initial State:
  Position: (0.00, 0.00, 5.00)
  Velocity: (0.00, 0.00, 0.00)
  Time: 0.00s

Using ML-based trajectory prediction

=== Trajectory Data Points ===
------------------------------------------------------------------------------------------------------------------------
Step    0 | t= 0.000s | Pos: (  0.000,   0.000,   5.000) | Vel: ( 0.000,  0.000,  0.000) | Speed:  0.000 m/s | Dist: 14.142 m
Step    1 | t= 0.100s | Pos: (  0.089,   0.089,   5.001) | Vel: ( 0.892,  0.892,  0.015) | Speed:  1.262 m/s | Dist: 13.916 m
Step    2 | t= 0.200s | Pos: (  0.267,   0.267,   5.004) | Vel: ( 1.781,  1.781,  0.031) | Speed:  2.518 m/s | Dist: 13.459 m
Step    3 | t= 0.300s | Pos: (  0.534,   0.534,   5.009) | Vel: ( 2.667,  2.667,  0.048) | Speed:  3.772 m/s | Dist: 12.770 m
Step    4 | t= 0.400s | Pos: (  0.889,   0.889,   5.016) | Vel: ( 3.550,  3.550,  0.067) | Speed:  5.021 m/s | Dist: 11.850 m
Step    5 | t= 0.500s | Pos: (  1.334,   1.334,   5.025) | Vel: ( 4.447,  4.447,  0.087) | Speed:  6.290 m/s | Dist: 10.698 m
Step    6 | t= 0.600s | Pos: (  1.867,   1.867,   5.036) | Vel: ( 5.331,  5.331,  0.109) | Speed:  7.538 m/s | Dist:  9.313 m
Step    7 | t= 0.700s | Pos: (  2.490,   2.490,   5.049) | Vel: ( 6.232,  6.232,  0.132) | Speed:  8.813 m/s | Dist:  7.697 m
...

✓ Reached waypoint 1 at t=2.345s
→ Moving to waypoint 2: (20, 5, 8)

Step   25 | t= 2.500s | Pos: ( 10.234,  10.123,   5.234) | Vel: ( 5.234,  1.234,  0.567) | Speed:  5.567 m/s | Dist: 12.456 m
Step   26 | t= 2.600s | Pos: ( 10.756,  10.234,   5.290) | Vel: ( 5.456,  1.345,  0.589) | Speed:  5.789 m/s | Dist: 11.890 m
...

✓ Reached waypoint 2 at t=5.678s
→ Moving to waypoint 3: (0, 0, 5)

...

✓ Reached waypoint 3 at t=9.123s

✓✓✓ All waypoints reached! ✓✓✓
------------------------------------------------------------------------------------------------------------------------

=== Simulation Complete ===
Total steps: 92
Total time: 9.2 seconds
Waypoints reached: 3/3

Final State:
  Position: (0.05, 0.03, 5.01)
  Velocity: (0.12, 0.08, 0.02)
  Time: 9.20s

Trajectory data saved to: trajectory_output.csv

✓ Demo complete!
```

---

### Step 6B: Summary Output Mode (if you chose 'n')

**You'll See:**
```
=== Starting Simulation ===
Initial State:
  Position: (0.00, 0.00, 5.00)
  Velocity: (0.00, 0.00, 0.00)
  Time: 0.00s

Using ML-based trajectory prediction

Step 0 | t=0.00s | Distance: 14.14m | Waypoint 1/3
Step 10 | t=1.00s | Distance: 8.23m | Waypoint 1/3
Step 20 | t=2.00s | Distance: 3.45m | Waypoint 1/3

✓ Reached waypoint 1 at t=2.345s
→ Moving to waypoint 2: (20, 5, 8)

Step 30 | t=3.00s | Distance: 11.67m | Waypoint 2/3
Step 40 | t=4.00s | Distance: 6.89m | Waypoint 2/3
Step 50 | t=5.00s | Distance: 2.34m | Waypoint 2/3

✓ Reached waypoint 2 at t=5.678s
→ Moving to waypoint 3: (0, 0, 5)

Step 60 | t=6.00s | Distance: 18.45m | Waypoint 3/3
Step 70 | t=7.00s | Distance: 11.23m | Waypoint 3/3
Step 80 | t=8.00s | Distance: 5.67m | Waypoint 3/3
Step 90 | t=9.00s | Distance: 1.23m | Waypoint 3/3

✓ Reached waypoint 3 at t=9.123s

✓✓✓ All waypoints reached! ✓✓✓

=== Simulation Complete ===
Total steps: 92
Total time: 9.2 seconds
Waypoints reached: 3/3

Final State:
  Position: (0.05, 0.03, 5.01)
  Velocity: (0.12, 0.08, 0.02)
  Time: 9.20s

Trajectory data saved to: trajectory_output.csv

✓ Demo complete!
```

---

## 📊 Understanding the Output

### Detailed Mode Column Explanation

```
Step    0 | t= 0.000s | Pos: (  0.000,   0.000,   5.000) | Vel: ( 0.000,  0.000,  0.000) | Speed:  0.000 m/s | Dist: 14.142 m
^^^^^      ^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^    ^^^^^^^^^^^^^^
  |            |                    |                                  |                           |                  |
Step #      Time        Position (x, y, z)              Velocity (x, y, z)                Speed            Distance to target
```

### What Each Value Means

| Field | Unit | Description |
|-------|------|-------------|
| **Step** | number | Simulation step count (increments by 1) |
| **t** | seconds | Time since simulation start |
| **Pos** | meters | Drone position in 3D space (x, y, z) |
| **Vel** | m/s | Velocity components in each axis |
| **Speed** | m/s | Total speed (magnitude of velocity vector) |
| **Dist** | meters | Euclidean distance to current target waypoint |

---

## 📈 CSV Output Preview

After running, you'll have `trajectory_output.csv`:

```csv
step,time,pos_x,pos_y,pos_z,vel_x,vel_y,vel_z,acc_x,acc_y,acc_z,speed,distance_to_target,target_x,target_y,target_z
0,0.000,0.000,0.000,5.000,0.000,0.000,0.000,0.000,0.000,0.000,0.000,14.142,10.000,10.000,5.000
1,0.100,0.089,0.089,5.001,0.892,0.892,0.015,8.920,8.920,0.150,1.262,13.916,10.000,10.000,5.000
2,0.200,0.267,0.267,5.004,1.781,1.781,0.031,8.890,8.890,0.160,2.518,13.459,10.000,10.000,5.000
3,0.300,0.534,0.534,5.009,2.667,2.667,0.048,8.860,8.860,0.170,3.772,12.770,10.000,10.000,5.000
...
```

Open this in Excel, Python, or MATLAB for analysis!

---

## 🎯 Sample Waypoint Patterns to Try

### Pattern 1: Simple Square
```
Waypoints: 4
1: 10 0 5
2: 10 10 5
3: 0 10 5
4: 0 0 5
Initial: 0 0 5
```

**Result**: Drone flies in a square pattern

---

### Pattern 2: Vertical Climb
```
Waypoints: 2
1: 0 0 10
2: 0 0 5
Initial: 0 0 5
```

**Result**: Drone climbs up and comes back down

---

### Pattern 3: Figure-8 (Approximate)
```
Waypoints: 8
1: 10 0 5
2: 5 5 7
3: 0 0 9
4: -5 5 7
5: -10 0 5
6: -5 -5 7
7: 0 0 9
8: 5 -5 7
Initial: 10 0 5
```

**Result**: Drone flies a 3D figure-8 pattern

---

## 🎨 Visual Trajectory Representation

### 2D Top View (X-Y Plane)

```
        Y
        ^
        |
   WP2  •  (20, 5)
        |
        |
   WP1  •  (10, 10)
        |    \
        |     \
        |      \
        |       • Start (0, 0)
        |      /
        |     /
   WP3  •  (0, 0)
        |
        +-------------> X
```

### 3D View

```
         Z (altitude)
         ^
         |     • WP2 (20, 5, 8)
     8m  |    /
         |   /
     5m  |  • WP1 (10, 10, 5)
         | /|\
         |/ | \
         •  |  • Start (0, 0, 5)
            |   \
            |    • WP3 (0, 0, 5)
            |
            +----------> X, Y (ground plane)
```

---

## 🔍 Interpreting the Results

### Normal Trajectory Behavior

**Acceleration Phase:**
```
Step 0-10: Speed increases from 0 to 8 m/s
Distance decreases steadily
```

**Cruise Phase:**
```
Step 10-40: Speed relatively constant (8-10 m/s)
Distance decreases linearly
```

**Deceleration Phase:**
```
Step 40-50: Speed decreases from 8 to 1 m/s
Distance approaches 0
```

**Waypoint Reached:**
```
✓ Reached waypoint 1 at t=2.345s
→ Moving to waypoint 2: (20, 5, 8)
```

---

## 💡 Tips for Best Experience

### 1. Choose Output Mode Wisely

**Detailed Mode** (`y`):
- ✅ See every single data point
- ✅ Best for debugging
- ✅ Best for short simulations (< 100 steps)
- ⚠️  Lots of console output
- ⚠️  Slower due to I/O

**Summary Mode** (`n`):
- ✅ Clean, readable output
- ✅ Fast simulation
- ✅ Good for long trajectories
- ✅ Still saves complete data to CSV
- ℹ️  Shows status every 1 second

### 2. Always Enable CSV Export

Even if you choose summary mode, enable CSV:
```
Do you want to save trajectory data to CSV? (y/n): y
```

This gives you complete data for later analysis without slowing down the simulation.

### 3. Good Waypoint Practices

✅ **Good spacing**: 5-20 meters apart  
✅ **Gradual altitude changes**: < 5m between waypoints  
✅ **Reasonable coordinates**: ±50m from origin  
❌ **Too close**: < 1m apart (reaches immediately)  
❌ **Too far**: > 50m apart (takes very long)  
❌ **Extreme altitudes**: > 100m or < 0m  

---

## 🎬 Complete Session Example

### Input
```
Mode: 1
Waypoints: 3
  1: 10 10 5
  2: 20 5 8  
  3: 0 0 5
Initial: 0 0 5
CSV: y
Detailed: n
```

### Output Summary
```
Steps taken: 92
Time elapsed: 9.2 seconds
Waypoints reached: 3/3
Output file: trajectory_output.csv
```

### Time Breakdown
- Waypoint 1: 2.3 seconds (23 steps)
- Waypoint 2: 3.4 seconds (34 steps)
- Waypoint 3: 3.5 seconds (35 steps)

---

## 📁 Where Files Are Located

After running:

```
/workspace/cpp/build/
├── drone_trajectory_cpp          ← Executable
└── trajectory_output.csv         ← Output data (if enabled)
```

---

## 🚀 Quick Command Reference

### Build and Run
```bash
cd /workspace/cpp/build
cmake .. && make
./drone_trajectory_cpp
```

### View CSV
```bash
cat trajectory_output.csv | head -20
```

### Count Data Points
```bash
wc -l trajectory_output.csv
```

### Visualize (requires Python)
```bash
python3 << 'EOF'
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('trajectory_output.csv')
plt.plot(df['time'], df['speed'])
plt.xlabel('Time (s)')
plt.ylabel('Speed (m/s)')
plt.title('Speed Profile')
plt.grid(True)
plt.show()
EOF
```

---

## ✅ Success Indicators

You know it's working when you see:

1. ✓ "ML model loaded successfully!" (or physics fallback message)
2. ✓ Waypoints listed correctly after input
3. ✓ Trajectory data points printing to console
4. ✓ "Reached waypoint X at t=Y.Ys" messages
5. ✓ "All waypoints reached!" final message
6. ✓ "Trajectory data saved to: trajectory_output.csv"

---

**Happy Flying! 🚁✨**

For more details, see:
- `QUICK_START_INTERACTIVE.md` - Detailed instructions
- `README_INTERACTIVE_MODE.md` - Technical documentation
- `START_HERE_INTERACTIVE_CPP.md` - Overview guide
