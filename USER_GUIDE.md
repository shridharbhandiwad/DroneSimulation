# 🚁 Drone Trajectory Simulation - User Guide

## 📖 Table of Contents
1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Creating Custom Trajectories](#creating-custom-trajectories)
4. [Simulation Controls](#simulation-controls)
5. [Tips & Tricks](#tips--tricks)
6. [Keyboard Shortcuts](#keyboard-shortcuts)

---

## 🚀 Getting Started

### Launch the Application
```bash
cd /workspace
python3 python/simulation.py
```

### First Launch
When you first open the application, you'll see:
- A 3D view with a grid (left side)
- Waypoint management panel (middle)
- FPV camera feed (right side)
- A random trajectory already generated and ready to play

---

## 🖥️ Interface Overview

### Layout Description

```
┌─────────────────────────────────────────────────────────────────┐
│                  Drone Trajectory Simulation Pro                 │
├───────────────┬─────────────────────┬───────────────────────────┤
│               │                     │                            │
│ 🚁 3D View    │ 📍 Waypoint Manager │ 📹 FPV Camera             │
│               │                     │                            │
│   (Large      │  ┌──────────────┐  │   ┌──────────────────┐    │
│    3D         │  │ ☑ Click Mode │  │   │                  │    │
│    Visual)    │  │ Height: 10m  │  │   │  Camera View     │    │
│               │  └──────────────┘  │   │  with HUD        │    │
│               │                     │   │                  │    │
│               │  Waypoints:         │   └──────────────────┘    │
│               │  • WP 1: (x,y,z)   │                            │
│               │  • WP 2: (x,y,z)   │                            │
│               │                     │                            │
│ ⚙️ Controls   │  📊 Telemetry       │                            │
│ [▶️][🔄][🎲] │  Position: (x,y,z)  │                            │
│ Speed: ━━●━   │  Velocity: (x,y,z)  │                            │
│               │  🤖 AI Status       │                            │
└───────────────┴─────────────────────┴───────────────────────────┘
```

### Panel Details

#### Left Panel - 3D Visualization
**Purpose**: Main visualization area
**Components**:
- Large 3D view with rotatable camera
- Grid representing ground plane
- Visual markers:
  - 🔴 Red sphere: Drone current position (15px)
  - 🔵 Blue spheres: Trajectory waypoints (12px)
  - 🟡 Gold spheres: Your custom waypoints (14px)
  - 🟢 Green line: Flight path (3px width)

**Controls Section**:
- `▶️ Play` button: Start simulation (Green)
- `🔄 Reset` button: Reset to beginning (Orange)
- `🎲 Random Trajectory` button: Generate random path (Purple)
- `Speed Slider`: Adjust playback speed (0.1x to 5.0x)

#### Middle Panel - Waypoint Manager
**Purpose**: Interactive waypoint control
**Components**:

1. **Click Mode Section**
   - `☑ Click to Add Waypoints`: Enable/disable click mode
   - `Click Height`: Slider (5-30m) to set waypoint altitude

2. **Waypoint List**
   - Shows all user-created waypoints
   - Format: `WP #: (x, y, z)`
   - Click to select, then remove

3. **Action Buttons**
   - `➖ Remove`: Delete selected waypoint
   - `🗑️ Clear All`: Clear all waypoints
   - `✨ Generate Trajectory`: Create path from waypoints (Teal)

4. **Telemetry Display**
   - Real-time position, velocity, acceleration
   - Current waypoint target
   - Simulation time and progress

5. **AI Status**
   - Shows if ML model is active (green ✓) or physics-only mode (orange ⚠)

#### Right Panel - FPV Camera
**Purpose**: First-person view from drone
**Display Elements**:
- Live camera feed from drone's perspective
- HUD overlay showing:
  - `ALT`: Altitude above ground
  - `POS`: Current X,Y position
  - `YAW`: Heading in degrees
  - `PITCH`: Pitch angle in degrees
- Green crosshair in center
- Sky (blue) and ground (green with grid) visualization

---

## 🎯 Creating Custom Trajectories

### Step-by-Step Tutorial

#### Method 1: Click and Fly

1. **Enable Click Mode**
   ```
   ✓ Click the "Click to Add Waypoints" checkbox
   → Cursor changes to crosshair
   → Status bar shows "Click mode enabled"
   ```

2. **Set Altitude**
   ```
   → Move the "Click Height" slider
   → Choose between 5m (low) to 30m (high)
   → Default: 10m (good for most scenarios)
   ```

3. **Place Waypoints**
   ```
   → Click anywhere in the 3D view
   → Gold sphere appears at clicked position
   → Waypoint added to list: "WP 1: (12.3, -5.7, 10.0)"
   → Repeat to add more waypoints
   ```

4. **Generate Trajectory**
   ```
   → Click "✨ Generate Trajectory" button
   → Green line appears connecting waypoints
   → Blue spheres mark calculated path
   → Status: "Generated trajectory with X waypoints"
   ```

5. **Fly the Path**
   ```
   → Click "▶️ Play" to start
   → Watch drone follow your custom path
   → Adjust speed with slider if needed
   ```

#### Method 2: Random Trajectory

1. **Quick Start**
   ```
   → Click "🎲 Random Trajectory"
   → Random waypoints generated (3-6 points)
   → Trajectory automatically created
   → Ready to play
   ```

### Waypoint Management

#### Adding Waypoints
- Click anywhere in 3D view when click mode is on
- Waypoint appears immediately
- Listed in waypoint list automatically

#### Removing Waypoints
1. Click on waypoint in the list to select it
2. Click "➖ Remove" button
3. Waypoint disappears from both list and 3D view

#### Clearing All
1. Click "🗑️ Clear All"
2. Confirmation dialog appears
3. Click "Yes" to confirm
4. All gold waypoints removed

#### Editing Strategy
- Add waypoints sequentially for smooth paths
- Remove and re-add to adjust positions
- Clear all and start over if needed

---

## 🎮 Simulation Controls

### Playback Controls

#### Play/Pause
- **Button**: `▶️ Play` / `⏸️ Pause`
- **Function**: Start or pause the simulation
- **State Changes**:
  - Playing: Button shows "⏸️ Pause" (green background)
  - Paused: Button shows "▶️ Play" (green background)
  - Status bar updates accordingly

#### Reset
- **Button**: `🔄 Reset`
- **Function**: Return to start of trajectory
- **Effect**: 
  - Drone returns to initial position
  - Time resets to 0
  - Simulation pauses automatically
  - Status: "Simulation reset"

#### Speed Control
- **Range**: 0.1x to 5.0x
- **Default**: 1.0x (real-time)
- **Recommendations**:
  - 0.1x - 0.5x: Slow motion, detailed observation
  - 1.0x - 2.0x: Normal to fast preview
  - 3.0x - 5.0x: Rapid testing, overview
- **Display**: Shows current multiplier (e.g., "2.5x")

### 3D View Controls

#### Mouse Controls
- **Left Drag**: Rotate view around drone
- **Right Drag**: Pan view horizontally/vertically
- **Scroll Wheel**: Zoom in/out
- **Click (when click mode on)**: Add waypoint

#### View Tips
- Rotate to see trajectory from different angles
- Zoom in for detail, zoom out for overview
- Pan to keep drone in view during flight

---

## 💡 Tips & Tricks

### Trajectory Design

#### For Smooth Flights
- Use 3-5 waypoints
- Space waypoints evenly
- Keep altitudes consistent (±5m variation)
- Avoid sharp direction changes

#### For Interesting Paths
- Mix different altitudes (5m to 30m)
- Create patterns (circle, figure-8, spiral)
- Use 6-8 waypoints for complex routes
- Combine high and low points

#### For Realistic Scenarios
- Start and end at similar altitudes
- Gradual altitude changes
- Wide turns (easier for drone physics)
- Test with different speeds

### Performance Optimization

#### Smooth Simulation
- Use moderate waypoint count (3-8)
- Avoid extreme altitude differences
- Keep trajectories within visible area (-30 to +30 units)

#### Visual Clarity
- Zoom to see entire trajectory
- Rotate view for best angle
- Use contrasting backgrounds (sky vs ground)

### Workflow Efficiency

#### Quick Testing
1. Click "🎲 Random Trajectory"
2. Set speed to 3.0x
3. Click "▶️ Play"
4. Observe overall behavior

#### Detailed Design
1. Enable click mode
2. Plan waypoint positions mentally
3. Place waypoints carefully
4. Generate and preview at 0.5x speed
5. Adjust as needed

#### Iterative Refinement
1. Generate trajectory
2. Play at normal speed
3. Identify issues
4. Remove problematic waypoints
5. Add corrected waypoints
6. Regenerate and test

---

## ⌨️ Status Bar Messages

The status bar (bottom of window) shows real-time feedback:

| Message | Meaning |
|---------|---------|
| "Click mode enabled..." | Waypoint clicking is active |
| "Click mode disabled" | Normal 3D navigation mode |
| "Added waypoint at (x,y,z)" | Waypoint successfully added |
| "Waypoint removed" | Selected waypoint deleted |
| "All waypoints cleared" | All waypoints removed |
| "Generated trajectory with X waypoints" | Custom trajectory created |
| "Generated random trajectory" | Random path created |
| "Simulation playing" | Playback started |
| "Simulation paused" | Playback paused |
| "Simulation reset" | Returned to start |
| "Simulation complete" | Reached end of trajectory |

---

## 🎨 Visual Guide

### Understanding the Colors

#### 3D View
- **Green Line** 🟢: The calculated flight path
- **Red Sphere** 🔴: Drone current position (moves during playback)
- **Blue Spheres** 🔵: Waypoints from generated trajectory
- **Gold Spheres** 🟡: Your manually placed waypoints
- **Gray Grid**: Ground reference plane

#### Buttons
- **Green** 🟢: Play/Pause (active simulation)
- **Blue** 🔵: Standard actions (generate, manage)
- **Orange** 🟠: Reset (return to start)
- **Purple** 🟣: Random generation
- **Teal** 🔷: Generate from waypoints

#### Status Indicators
- **Green ✓**: ML model active (AI-enhanced)
- **Orange ⚠**: Physics mode (no ML)
- **Teal values**: Real-time telemetry data
- **Dark gray**: Labels and titles

### Reading the Telemetry

```
Position:    (12.5, -3.2, 10.0)  ← X, Y, Z coordinates
Velocity:    (2.1, 0.5, 0.0) m/s ← Speed in each direction
Acceleration:(0.3, -0.1, 0.0) m/s² ← Rate of change
Current WP:  #3 (15.0, 10.0, 12.0) ← Target waypoint
Time:        5.2s ← Elapsed simulation time
Progress:    52/100 (52.0%) ← Step count and percentage
```

---

## 🐛 Common Issues & Solutions

### Issue: Waypoints not appearing
**Solution**: 
- Ensure click mode is enabled (checkbox checked)
- Check cursor is crosshair
- Try clicking in center of 3D view
- Verify waypoint height is within view (adjust camera zoom)

### Issue: Trajectory looks jagged
**Solution**:
- Add more waypoints for smoother curves
- Ensure waypoints are evenly spaced
- Check physics settings are correct
- Try regenerating trajectory

### Issue: Drone moves too fast/slow
**Solution**:
- Adjust speed slider (left side)
- For observation: use 0.5x - 1.0x
- For testing: use 2.0x - 3.0x
- Maximum is 5.0x

### Issue: Can't see entire trajectory
**Solution**:
- Zoom out with mouse scroll wheel
- Rotate view to better angle
- Resize window to 1600x900 or larger
- Pan view to center trajectory

### Issue: Removed wrong waypoint
**Solution**:
- Click mode still enabled - re-add it
- Or clear all and recreate
- No undo feature (yet!)

---

## 🏆 Best Practices

1. **Start Simple**: Begin with 3-4 waypoints, get comfortable with the tool
2. **Save Mental Notes**: Remember good waypoint configurations (no save feature yet)
3. **Use Status Bar**: Read feedback messages for confirmation
4. **Experiment**: Try different heights, speeds, and patterns
5. **Preview**: Always preview at slow speed before full speed
6. **Iterate**: Refine trajectories through multiple generations

---

## 🎓 Learning Exercises

### Exercise 1: Basic Flight
1. Place 3 waypoints in a line
2. All at same height (10m)
3. Generate and play at 1.0x speed
4. Observe smooth linear flight

### Exercise 2: Altitude Change
1. Place 4 waypoints
2. Heights: 5m, 15m, 25m, 10m
3. Generate and observe climb/descent
4. Note how drone handles altitude changes

### Exercise 3: Complex Pattern
1. Create a square pattern (4 waypoints)
2. Add a center point (5th waypoint)
3. Generate star pattern
4. Experiment with different orders

### Exercise 4: Speed Comparison
1. Generate any trajectory
2. Play at 0.5x speed - observe details
3. Reset and play at 2.0x - see overview
4. Compare camera views at different speeds

---

## 📚 Additional Resources

- `FEATURE_UPDATE.md` - Detailed feature documentation
- `BEFORE_AFTER_COMPARISON.md` - See what's changed
- `README.md` - Project overview
- Python source: `python/simulation.py`

---

## 🤝 Getting Help

If you encounter issues:
1. Check this guide first
2. Review status bar messages
3. Try resetting and starting fresh
4. Check console for error messages

---

**Happy Flying! 🚁✨**

*Enjoy your enhanced drone trajectory simulation!*
