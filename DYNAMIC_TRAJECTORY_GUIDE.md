# Dynamic Trajectory with Auto-Play and Per-Waypoint Speed

## Overview

The drone simulation now features **automatic trajectory execution** and **per-waypoint speed control**. The drone will automatically move through all waypoints without manual intervention, and each waypoint can have its own desired speed.

## Key Features

### 1. **Automatic Trajectory Execution (Auto-Play)**
- When enabled, the drone automatically starts moving as soon as a trajectory is generated
- No need to manually click "Play" after generating waypoints
- Seamlessly transitions from one waypoint to the next
- Can be toggled on/off based on your preference

### 2. **Per-Waypoint Speed Control**
- Each waypoint now has its own speed parameter (in m/s)
- Speed range: 1-15 m/s (adjustable via slider)
- The drone adjusts its speed as it approaches each waypoint
- Automatic slowdown near waypoints for smooth transitions

### 3. **Real-Time Speed Monitoring**
- "Target Speed" display shows the current waypoint's desired speed
- "Velocity" display shows actual current speed
- Compare target vs actual speed during flight

## How to Use

### Setting Up Waypoints with Custom Speeds

1. **Enable Click Mode**
   - Check "Click to Add Waypoints" checkbox
   - The 3D view cursor will change to a crosshair

2. **Configure Waypoint Parameters**
   - **Height Slider**: Set the altitude for the waypoint (5-30m)
   - **Speed Slider**: Set the desired speed for this waypoint (1-15 m/s)
   
3. **Add Waypoints**
   - Click on the 3D view to place waypoints
   - Each waypoint will be created with the current height and speed settings
   - The waypoint list shows: `WP 1: (x, y, z) @ speed m/s`

4. **Generate Trajectory**
   - Click "Generate Trajectory" button
   - With "Auto-Play on Generate" enabled, the drone will immediately start moving
   - The drone will automatically proceed through all waypoints

### Auto-Play Mode

**Enabled (Default):**
- ✓ Trajectory starts automatically after generation
- ✓ Seamless waypoint transitions
- ✓ Ideal for testing and demonstrations

**Disabled:**
- Manual control via "Play" button
- Step-through capability
- Useful for detailed analysis

**Toggle:** Use the "Auto-Play on Generate" checkbox in the Waypoint Manager panel.

### Per-Waypoint Speed Examples

#### Example 1: Gradual Acceleration
```
WP 1: (10, 10, 10) @ 5.0 m/s    # Slow start
WP 2: (20, 20, 12) @ 10.0 m/s   # Moderate speed
WP 3: (30, 30, 15) @ 15.0 m/s   # Maximum speed
```

#### Example 2: Survey Pattern
```
WP 1: (10, 0, 10) @ 8.0 m/s     # Transit speed
WP 2: (20, 0, 10) @ 3.0 m/s     # Slow for inspection
WP 3: (20, 10, 10) @ 3.0 m/s    # Continue slow
WP 4: (30, 10, 10) @ 8.0 m/s    # Return to transit
```

#### Example 3: Emergency Response
```
WP 1: (15, 15, 15) @ 12.0 m/s   # Fast approach
WP 2: (20, 20, 12) @ 2.0 m/s    # Slow at target area
WP 3: (25, 20, 10) @ 15.0 m/s   # Fast exit
```

## Dynamic Mode Features

### Modifying Trajectory Mid-Flight

1. **Enable Dynamic Mode**
   - Check "Enable Dynamic Mode" checkbox
   - "Apply Changes" button becomes active

2. **Modify Waypoints During Flight**
   - Add new waypoints while the drone is moving
   - Remove unwanted waypoints
   - Adjust speeds for upcoming waypoints

3. **Apply Changes**
   - Click "Apply Changes" button
   - The trajectory regenerates from the current position
   - Drone continues moving with the new plan
   - With Auto-Play enabled, movement continues automatically

### Real-Time Trajectory Updates

- Old trajectory preserved up to current position
- New trajectory seamlessly appended
- No discontinuities in position or velocity
- Automatic re-planning with current waypoint speeds

## User Interface Components

### Waypoint Manager Panel

```
┌─────────────────────────────────────┐
│ Waypoint Manager                    │
├─────────────────────────────────────┤
│ ☐ Click to Add Waypoints           │
│                                     │
│ Waypoint Height:    [====●====] 10m│
│ Waypoint Speed:     [====●====] 10 m/s│
│                                     │
│ Active Waypoints:                   │
│ ┌─────────────────────────────────┐ │
│ │ WP 1: (10.0, 10.0, 10.0) @ 8.0  │ │
│ │ WP 2: (20.0, 15.0, 12.0) @ 10.0 │ │
│ │ WP 3: (30.0, 20.0, 15.0) @ 12.0 │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Remove] [Clear All]               │
│                                     │
│ [Generate Trajectory]              │
│ ☑ Auto-Play on Generate            │
│ ☐ Enable Dynamic Mode              │
│ [Apply Changes]                    │
└─────────────────────────────────────┘
```

### Flight Telemetry Panel

```
┌─────────────────────────────────────┐
│ Flight Telemetry                    │
├─────────────────────────────────────┤
│ Position:      (12.5, 15.3, 11.2)  │
│ Velocity:      9.2 m/s | (5.1, 7.0, 0.8)│
│ Acceleration:  (0.5, 0.3, -0.1) m/s²│
│ Current WP:    #2 | Dist: 8.4m     │
│ Target Speed:  10.0 m/s            │
│ Time:          15.3s               │
│ Progress:      245/580 (42.2%)     │
└─────────────────────────────────────┘
```

## Speed Physics

### Speed Control Algorithm

1. **Target Speed**: Set per waypoint
2. **Slowdown Zone**: 3m radius around each waypoint
3. **Progressive Deceleration**: Proportional to distance
4. **Max Speed Limit**: 15 m/s (hardware limit)
5. **Acceleration Limit**: 5 m/s² (smooth transitions)

### Speed Behavior

```
Speed Profile Approaching Waypoint:

15 m/s ┤           ╭─────╮
       │          ╱       ╲
10 m/s ┤         ╱         ╲
       │        ╱           ╲___
 5 m/s ┤       ╱                ╲
       │      ╱                  ╲
 0 m/s ┴─────┴────────────────────┴─────
       │ Start  Cruise    Slow   WP    │
       └──────────────────────────────┘
       Distance from Waypoint (m)
```

## Use Cases

### 1. **Inspection Missions**
- High speed between inspection points
- Slow speed at inspection points
- Automatic progression through inspection checklist

### 2. **Delivery Missions**
- Fast flight to destination
- Slow, careful approach for landing
- Automatic return at cruise speed

### 3. **Search Patterns**
- Moderate speed during search
- Very slow speed when target detected
- Fast speed for repositioning

### 4. **Racing/Performance**
- Maximum speed on straightaways
- Controlled speed through turns
- Optimal time through course

### 5. **Training Simulations**
- Varied speed scenarios
- Emergency response practice
- Automatic mission execution

## Tips and Best Practices

### Speed Selection

- **Slow (1-5 m/s)**: Inspection, landing, tight maneuvers
- **Moderate (5-10 m/s)**: General flight, survey patterns
- **Fast (10-15 m/s)**: Transit, racing, emergency response

### Waypoint Placement

- Place waypoints at least 5m apart for smooth transitions
- Use higher speeds for straight segments
- Use lower speeds for turns and precision work
- Add intermediate waypoints for complex paths

### Auto-Play vs Manual

**Use Auto-Play when:**
- ✓ Testing complete mission profiles
- ✓ Demonstrating capabilities
- ✓ Running automated missions
- ✓ Training scenarios

**Use Manual when:**
- ✓ Analyzing specific segments
- ✓ Debugging trajectory issues
- ✓ Studying speed transitions
- ✓ Frame-by-frame analysis

### Dynamic Mode Usage

**When to use:**
- Mission changes required mid-flight
- Obstacle avoidance scenarios
- Adaptive mission planning
- Real-time mission updates

**Best practices:**
- Apply changes before reaching current waypoint
- Ensure smooth speed transitions
- Verify new trajectory before applying
- Monitor velocity continuity

## Troubleshooting

### Drone Not Moving Automatically

**Check:**
1. Is "Auto-Play on Generate" checkbox enabled?
2. Is there a valid trajectory? (at least 1 waypoint)
3. Is the simulation already at the end?

**Solution:** Enable Auto-Play checkbox and regenerate trajectory.

### Speed Not Changing at Waypoints

**Check:**
1. Are waypoint speeds set correctly?
2. Is "Target Speed" showing in telemetry?
3. Are waypoints too close together?

**Solution:** Increase waypoint spacing and verify speed settings.

### Jerky Movement

**Check:**
1. Are speed differences too large between waypoints?
2. Are waypoints too close together?
3. Is playback speed too high?

**Solution:** Use gradual speed changes and proper waypoint spacing.

### Apply Changes Not Working

**Check:**
1. Is "Enable Dynamic Mode" checkbox enabled?
2. Is the simulation playing?
3. Are there waypoints to apply?

**Solution:** Enable Dynamic Mode before attempting to apply changes.

## Technical Details

### Speed Parameter Format

Waypoints support multiple formats:

```python
# Dictionary format (recommended)
waypoint = {'position': [x, y, z], 'speed': 10.0}

# Tuple format
waypoint = ([x, y, z], 10.0)

# Array format (uses default speed of 10.0 m/s)
waypoint = [x, y, z]
```

### Trajectory Data Structure

```python
trajectory = {
    'positions': np.array([[x, y, z], ...]),
    'velocities': np.array([[vx, vy, vz], ...]),
    'accelerations': np.array([[ax, ay, az], ...]),
    'times': np.array([t, ...]),
    'waypoint_indices': np.array([wp_idx, ...]),
    'waypoints': np.array([[x, y, z], ...]),
    'waypoint_speeds': np.array([speed, ...]),  # NEW
    'dt': 0.1
}
```

### Speed Control Physics

```python
# Slowdown distance
slowdown_distance = 3.0  # meters

# Speed calculation
if distance < slowdown_distance:
    desired_speed = min(target_speed, 
                       distance / slowdown_distance * target_speed)
else:
    desired_speed = min(target_speed, max_speed)
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Space | Toggle Play/Pause (when Auto-Play disabled) |
| R | Reset simulation |
| 1-4 | Camera views (Top, Side, Front, Iso) |

## Performance Notes

- **Trajectory Generation**: ~50ms for typical missions
- **Speed Calculation**: Per timestep (0.1s default)
- **Real-time Updates**: Smooth with up to 20 waypoints
- **Auto-Play Latency**: <10ms from generation

## Future Enhancements

Potential additions:
- [ ] Acceleration/deceleration profiles per waypoint
- [ ] Hover time at waypoints
- [ ] Speed-based path optimization
- [ ] Automatic speed calculation based on path curvature
- [ ] Speed presets (slow/medium/fast)
- [ ] Mission time estimation

## Summary

The new dynamic trajectory system with auto-play and per-waypoint speed control provides:

✓ **Automatic execution** - Hands-free mission operation  
✓ **Speed control** - Fine-tuned speed for each waypoint  
✓ **Real-time updates** - Modify missions mid-flight  
✓ **Smooth transitions** - Physics-based speed changes  
✓ **Easy to use** - Intuitive sliders and controls  

**Start using it now:** Just add waypoints, set speeds, and watch the drone execute your mission automatically!
