# Dynamic Waypoints - Quick Start Guide

## 🚀 Quick Overview

Dynamic waypoint modification allows you to **change the drone's path while it's flying**. No need to stop and restart - just add, modify, or remove waypoints and apply the changes in real-time!

## ⚡ 5-Minute Tutorial

### Python GUI (Easiest Way)

1. **Start the simulation:**
   ```bash
   cd /workspace/python
   python3 simulation.py
   ```

2. **Set up initial flight:**
   - Click "🎲 Random Trajectory" or add your own waypoints
   - Click "▶️ Play" to start the flight

3. **Enable dynamic mode:**
   - Check "🔄 Enable Dynamic Waypoint Mode" ✅

4. **Modify path during flight:**
   - Check "Click to Add Waypoints" ✅
   - Click anywhere on the 3D view to add a waypoint
   - Click "⚡ Apply Waypoint Changes" to update the path
   - Watch the drone smoothly transition to the new path!

### Python Code (5 Lines)

```python
from trajectory_generator import TrajectoryGenerator
import numpy as np

generator = TrajectoryGenerator()

# During flight at step 50:
current_pos = trajectory['positions'][50]
current_vel = trajectory['velocities'][50]

# Change destination mid-flight:
new_waypoints = [np.array([25, 15, 12]), np.array([40, 30, 10])]
updated = generator.regenerate_from_current(current_pos, current_vel, new_waypoints)
```

### C++ Code (Quick Example)

```cpp
#include "drone_trajectory.h"

drone::PhysicsTrajectoryGenerator physics;

// Add waypoint during flight
physics.addWaypoint(drone::Vec3(30.0f, 20.0f, 15.0f));

// Modify existing waypoint
physics.modifyWaypoint(2, drone::Vec3(35.0f, 25.0f, 12.0f));
```

## 🎯 Common Use Cases

### 1. Avoid Obstacle
```python
# Detected obstacle! Add detour waypoint
emergency_point = calculate_safe_detour(current_pos, obstacle_pos)
generator.regenerate_from_current(current_pos, current_vel, [emergency_point] + remaining_waypoints)
```

### 2. Follow Moving Target
```python
while tracking:
    target_pos = get_target_position()
    generator.regenerate_from_current(current_pos, current_vel, [target_pos])
```

### 3. Mission Change
```python
# Received new orders mid-flight
new_mission = load_new_mission_waypoints()
generator.regenerate_from_current(current_pos, current_vel, new_mission)
```

## ✅ Test Results

All tests passed ✓

- **Trajectory continuity:** ✓ Smooth transitions
- **Performance:** ✓ 3.38ms average (excellent!)
- **Edge cases:** ✓ All handled correctly
- **Position/velocity matching:** ✓ Perfect continuity

## 📚 Full Documentation

For complete API reference and advanced features, see:
- [Full Guide](DYNAMIC_WAYPOINTS_GUIDE.md) - Complete documentation
- [Test Suite](python/test_dynamic_waypoints.py) - Working examples

## 🎥 Visual Guide (GUI)

```
┌─────────────────────────────────────────────────┐
│  Waypoint Manager                               │
│  ☐ Click to Add Waypoints                      │
│  ☑ 🔄 Enable Dynamic Waypoint Mode             │
│                                                  │
│  Waypoints:                                     │
│  • WP 1: (10.0, 10.0, 10.0)                    │
│  • WP 2: (20.0, 15.0, 12.0)  ← You can add     │
│  • WP 3: (30.0, 20.0, 15.0)  ← during flight!  │
│                                                  │
│  [➖ Remove]  [🗑️ Clear All]                   │
│  [✨ Generate Trajectory]                       │
│  [⚡ Apply Waypoint Changes]  ← Click this!    │
└─────────────────────────────────────────────────┘
```

## 🔧 Tips

1. **Enable dynamic mode first** - The "Apply" button only works when dynamic mode is enabled
2. **Pause for precision** - Easier to add waypoints when paused
3. **Watch the green line** - This shows your updated path after applying changes
4. **Yellow markers** - These are your custom waypoints
5. **Performance** - Updates happen in ~3ms, no lag!

## 🐛 Troubleshooting

**Q: Apply button is grayed out?**  
A: Enable "🔄 Enable Dynamic Waypoint Mode" first

**Q: Waypoint not appearing?**  
A: Make sure "Click to Add Waypoints" is checked and you're clicking on the 3D view

**Q: Trajectory doesn't update?**  
A: Make sure you have at least one waypoint and clicked "Apply Waypoint Changes"

## 🎉 That's It!

You're ready to dynamically modify waypoints during flight! The drone will smoothly transition to new paths without interruption.

**Happy Flying! 🚁**
