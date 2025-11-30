# Dynamic Waypoint Modification Guide

## Overview

This feature allows you to add, modify, or remove waypoints **while the trajectory is already running**. This gives you the flexibility to change the drone's path during flight, enabling real-time path adaptation based on dynamic conditions.

## Features

### 1. **Real-time Path Modification**
- Add new waypoints during flight
- Remove waypoints from the current path
- Modify existing waypoint positions
- Regenerate trajectory from current position with new waypoints

### 2. **Seamless Trajectory Updates**
- The drone continues from its current position when waypoints are updated
- Trajectory is recalculated in real-time maintaining velocity continuity
- Visual feedback shows the updated path immediately

### 3. **Available in Both Python and C++**
- Python implementation with GUI support
- C++ implementation for high-performance applications

---

## Python Usage (Simulation GUI)

### Step-by-Step Guide

#### 1. **Start the Simulation**
```bash
cd /workspace/python
python simulation.py
```

#### 2. **Enable Dynamic Waypoint Mode**
- In the **Waypoint Manager** panel, check the box: **"🔄 Enable Dynamic Waypoint Mode"**
- This enables the "⚡ Apply Waypoint Changes" button
- Status message confirms: "Dynamic waypoint mode enabled"

#### 3. **Create Initial Trajectory**
- Option A: Click "🎲 Random Trajectory" for a random path
- Option B: Add custom waypoints and click "✨ Generate Trajectory"

#### 4. **Start Flight**
- Click "▶️ Play" to start the trajectory execution
- Watch the drone follow the path in the 3D view

#### 5. **Modify Path During Flight**

**Adding Waypoints:**
1. Check "Click to Add Waypoints"
2. Set desired height using the "Click Height" slider
3. Click on the 3D view to add waypoint at that position
4. The waypoint appears as a yellow marker

**Removing Waypoints:**
1. Select a waypoint from the list
2. Click "➖ Remove" to delete it

**Apply Changes:**
- Click "⚡ Apply Waypoint Changes" to regenerate trajectory
- The drone smoothly transitions to the new path from its current position
- The 3D view updates to show the new trajectory

#### 6. **Visual Feedback**
- **Red Marker**: Current drone position
- **Yellow Markers**: User-defined waypoints
- **Blue Markers**: Original trajectory waypoints
- **Green Line**: Trajectory path

---

## Python API Usage

### TrajectoryGenerator Class

```python
from trajectory_generator import TrajectoryGenerator
import numpy as np

# Initialize generator
generator = TrajectoryGenerator(dt=0.1)

# Generate initial trajectory
initial_pos = np.array([0, 0, 5])
initial_vel = np.array([0, 0, 0])
waypoints = [
    np.array([10, 10, 10]),
    np.array([20, 5, 15]),
    np.array([30, 20, 12])
]

trajectory = generator.generate(initial_pos, initial_vel, waypoints)

# During flight: Get current state at step 50
current_pos = trajectory['positions'][50]
current_vel = trajectory['velocities'][50]

# Modify waypoints during flight
new_waypoints = [
    np.array([25, 15, 12]),  # New waypoint 1
    np.array([35, 25, 10]),  # New waypoint 2
    np.array([40, 30, 8])    # New waypoint 3
]

# Regenerate trajectory from current position
new_trajectory = generator.regenerate_from_current(
    current_position=current_pos,
    current_velocity=current_vel,
    waypoints=new_waypoints,
    current_waypoint_idx=0
)
```

### Dynamic Waypoint Management Methods

```python
# Add waypoint to generator's internal list
generator.add_waypoint_at_index(np.array([15, 15, 10]), index=-1)  # Append

# Insert at specific position
generator.add_waypoint_at_index(np.array([5, 5, 8]), index=1)

# Remove waypoint
generator.remove_waypoint(index=2)

# Modify existing waypoint
generator.modify_waypoint(index=0, new_position=np.array([12, 12, 11]))

# Get current waypoints
waypoints = generator.get_waypoints()

# Set all waypoints at once
generator.set_waypoints(new_waypoints)

# Clear all waypoints
generator.waypoints.clear()
```

---

## C++ Usage

### Header Include

```cpp
#include "drone_trajectory.h"
```

### TrajectoryPredictor Example

```cpp
using namespace drone;

// Initialize predictor
TrajectoryPredictor predictor("model.onnx", "normalization.txt");
predictor.initialize();

// Set initial waypoints
std::vector<Vec3> waypoints = {
    Vec3(10.0f, 10.0f, 10.0f),
    Vec3(20.0f, 5.0f, 15.0f),
    Vec3(30.0f, 20.0f, 12.0f)
};
predictor.setWaypoints(waypoints);

// During flight: Add new waypoint
predictor.addWaypoint(Vec3(40.0f, 25.0f, 15.0f));

// Insert waypoint at specific index
predictor.insertWaypoint(Vec3(15.0f, 12.0f, 11.0f), 1);

// Modify existing waypoint
predictor.modifyWaypoint(2, Vec3(25.0f, 8.0f, 14.0f));

// Remove waypoint
predictor.removeWaypoint(1);

// Get current target waypoint
Vec3 target = predictor.getCurrentTargetWaypoint();

// Get current waypoint index
size_t idx = predictor.getCurrentWaypointIndex();

// Set current waypoint index (skip to specific waypoint)
predictor.setCurrentWaypointIndex(2);

// Clear all waypoints
predictor.clearWaypoints();
```

### PhysicsTrajectoryGenerator Example

```cpp
// Same interface as TrajectoryPredictor
PhysicsTrajectoryGenerator physics_gen(15.0f, 5.0f, 5.0f);

// Set waypoints
std::vector<Vec3> waypoints = {
    Vec3(10.0f, 10.0f, 10.0f),
    Vec3(20.0f, 5.0f, 15.0f)
};
physics_gen.setWaypoints(waypoints);

// Add waypoint during flight
physics_gen.addWaypoint(Vec3(30.0f, 15.0f, 12.0f));

// Get and use current target
Vec3 target = physics_gen.getCurrentTargetWaypoint();

DroneState current_state;
current_state.position = Vec3(5.0f, 5.0f, 8.0f);
current_state.velocity = Vec3(2.0f, 2.0f, 0.5f);

DroneState next_state;
physics_gen.update(current_state, target, 0.1f, next_state);
```

---

## Use Cases

### 1. **Obstacle Avoidance**
```python
# Detect obstacle in path
if obstacle_detected:
    # Add detour waypoint
    detour_point = calculate_detour(current_pos, obstacle_pos)
    user_waypoints.insert(0, detour_point)
    apply_waypoint_changes()
```

### 2. **Target Tracking**
```python
# Update waypoint to follow moving target
while tracking_target:
    target_pos = get_target_position()
    generator.modify_waypoint(0, target_pos)
    new_trajectory = generator.regenerate_from_current(
        current_pos, current_vel, [target_pos]
    )
```

### 3. **Mission Replanning**
```python
# Change mission mid-flight
new_mission_waypoints = load_new_mission()
generator.set_waypoints(new_mission_waypoints)
trajectory = generator.regenerate_from_current(
    current_pos, current_vel, new_mission_waypoints
)
```

### 4. **Manual Override**
```python
# Allow operator to add waypoint via click during flight
def on_user_click(position):
    if dynamic_mode_enabled:
        user_waypoints.append(position)
        # Prompt to apply changes
        show_apply_button()
```

---

## Technical Details

### Trajectory Regeneration Process

1. **Capture Current State**
   - Position, velocity, and acceleration at current timestep
   - Current waypoint index

2. **Filter Waypoints**
   - Remove already-reached waypoints
   - Keep only future waypoints

3. **Generate New Trajectory**
   - Start from current position and velocity
   - Apply physics/ML model to reach new waypoints

4. **Merge Trajectories**
   - Keep old trajectory up to current point
   - Append new trajectory from current point onward
   - Maintain time continuity

### Performance Considerations

- **Regeneration Time**: ~10-50ms for typical trajectories
- **No Flight Interruption**: Drone continues smoothly during update
- **Memory Efficient**: Only stores necessary history

### Thread Safety (C++)

```cpp
// For multi-threaded applications, protect waypoint modifications
std::mutex waypoint_mutex;

void addWaypointThreadSafe(const Vec3& waypoint) {
    std::lock_guard<std::mutex> lock(waypoint_mutex);
    predictor.addWaypoint(waypoint);
}
```

---

## Limitations and Considerations

1. **Physics Constraints**
   - Trajectory respects max speed and acceleration limits
   - Sharp turns may take longer than expected

2. **Minimum Waypoint Distance**
   - Waypoints too close to current position may be filtered out
   - Recommended minimum distance: 0.5m

3. **Trajectory Length**
   - Maximum trajectory time: 60 seconds (configurable)
   - Can regenerate multiple times during long missions

4. **UI Responsiveness**
   - Apply changes while paused for precise modifications
   - Changes can be applied during playback but may be harder to visualize

---

## Troubleshooting

### Problem: "Apply Waypoint Changes" button is disabled
**Solution**: Enable "🔄 Enable Dynamic Waypoint Mode" checkbox first

### Problem: Waypoint not appearing in 3D view
**Solution**: Check that waypoint height is within reasonable range (5-30m)

### Problem: Trajectory doesn't update after clicking "Apply"
**Solution**: 
- Ensure at least one waypoint exists
- Check that trajectory has been generated first
- Verify dynamic mode is enabled

### Problem: Drone makes sharp turns
**Solution**: 
- Add intermediate waypoints for smoother path
- Increase distance between waypoints
- Reduce max acceleration in physics parameters

---

## Examples

### Complete Example: Real-time Mission Adjustment

```python
import numpy as np
from trajectory_generator import TrajectoryGenerator

# Initialize
generator = TrajectoryGenerator(dt=0.1)

# Start with initial mission
initial_waypoints = [
    np.array([10, 0, 10]),
    np.array([20, 0, 10]),
    np.array([30, 0, 10])
]

trajectory = generator.generate(
    np.array([0, 0, 5]),
    np.array([0, 0, 0]),
    initial_waypoints
)

# Simulate flight to step 100
current_step = 100
current_pos = trajectory['positions'][current_step]
current_vel = trajectory['velocities'][current_step]

# Mission change: New target area detected
new_waypoints = [
    np.array([25, 10, 12]),  # Divert to new area
    np.array([30, 20, 15]),
    np.array([40, 20, 10])
]

# Regenerate from current position
updated_trajectory = generator.regenerate_from_current(
    current_pos,
    current_vel,
    new_waypoints
)

print(f"Original trajectory: {len(trajectory['positions'])} points")
print(f"Updated trajectory: {len(updated_trajectory['positions'])} points")
print(f"Smooth transition from: {current_pos}")
```

---

## API Reference

### Python TrajectoryGenerator Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `regenerate_from_current` | `current_position`, `current_velocity`, `waypoints`, `current_waypoint_idx`, `max_time` | `Dict` | Regenerate trajectory from current state |
| `add_waypoint_at_index` | `waypoint`, `index` | `None` | Add waypoint at index |
| `remove_waypoint` | `index` | `None` | Remove waypoint |
| `modify_waypoint` | `index`, `new_position` | `None` | Modify waypoint position |
| `get_waypoints` | - | `List[np.ndarray]` | Get current waypoints |
| `set_waypoints` | `waypoints` | `None` | Set all waypoints |

### C++ TrajectoryPredictor/PhysicsTrajectoryGenerator Methods

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `setWaypoints` | `const std::vector<Vec3>&` | `void` | Set all waypoints |
| `addWaypoint` | `const Vec3&` | `void` | Add waypoint at end |
| `insertWaypoint` | `const Vec3&`, `size_t` | `void` | Insert at index |
| `removeWaypoint` | `size_t` | `bool` | Remove at index |
| `modifyWaypoint` | `size_t`, `const Vec3&` | `bool` | Modify at index |
| `clearWaypoints` | - | `void` | Clear all waypoints |
| `getWaypoints` | - | `const std::vector<Vec3>&` | Get waypoints |
| `getCurrentWaypointIndex` | - | `size_t` | Get current index |
| `setCurrentWaypointIndex` | `size_t` | `void` | Set current index |
| `getCurrentTargetWaypoint` | - | `Vec3` | Get current target |

---

## Future Enhancements

- Real-time collision detection and avoidance
- Automatic path smoothing after waypoint changes
- Waypoint priority system
- Batch waypoint updates with single regeneration
- Undo/redo functionality for waypoint changes
- Waypoint templates and presets

---

## Related Documentation

- [Trajectory Generator API](trajectory_generator.py)
- [Simulation User Guide](simulation.py)
- [C++ API Documentation](cpp/drone_trajectory.h)
- [Physics Model Documentation](PHYSICS_MODEL.md)

---

## Support

For questions or issues related to dynamic waypoint modification:
1. Check this guide first
2. Review the example code
3. Test with simple scenarios before complex missions
4. Check console output for error messages

---

## Version History

- **v1.0** (Current): Initial implementation with full Python/C++ support
  - Real-time waypoint add/remove/modify
  - Seamless trajectory regeneration
  - GUI integration with visual feedback
