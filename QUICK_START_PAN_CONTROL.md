# Quick Start: Pan Control in 3D Trajectory Window

## 🎮 New Feature: Right Mouse Button Pan

The 3D trajectory visualization now supports pan control with the right mouse button!

## How to Use

### 1. Start the Simulation
```bash
cd /workspace
python3 python/simulation.py
```

### 2. Use Pan Control

**Right Mouse Button + Drag** = Pan the view

- Hold down the **right mouse button**
- Move your mouse to pan in any direction
- Release to stop panning

### 3. Complete Controls

| Control | Action |
|---------|--------|
| **Left Mouse + Drag** | Rotate the view |
| **Right Mouse + Drag** | Pan the view |
| **Mouse Wheel** | Zoom in/out |

### 4. Click Mode (Adding Waypoints)

When "🖱️ Click to Add Waypoints" is enabled:
- **Left Mouse Click** = Add waypoint at that location
- **Right Mouse + Drag** = Still pans (doesn't add waypoints)

## Tips & Tricks

### 🎯 Precise Navigation
1. **Zoom in** using mouse wheel
2. **Pan** with right mouse to center on area of interest
3. **Rotate** with left mouse for best viewing angle

### 🔄 Reset View
Use the camera preset buttons to reset:
- **⬆ Top** - Top-down view
- **↔ Side** - Side view
- **⬌ Front** - Front view
- **🔲 Isometric** - 45° angle view

### 📍 Follow Drone
Enable **"Follow Drone"** checkbox to automatically track the drone during playback (pan control still works!)

## Common Use Cases

### Viewing Large Trajectories
1. Zoom out to see full path
2. Pan to interesting sections
3. Zoom in for detail

### Comparing Waypoints
1. Pan to first waypoint
2. Rotate to best angle
3. Pan to next waypoint (view angle preserved)

### Debugging Trajectories
1. Pan to problem area
2. Enable click mode
3. Add corrective waypoints

## Demo

### Before Pan Control
- Could only rotate and zoom
- Hard to center on specific areas
- Required multiple rotations to navigate

### With Pan Control ✅
- Direct navigation to any area
- Smooth, intuitive camera movement
- Industry-standard 3D viewer controls

## Compatibility

✅ Works with all themes (White, Black, Monochrome)  
✅ Compatible with waypoint clicking  
✅ Preserves rotation and zoom  
✅ Works with "Follow Drone" mode  
✅ Functions with all camera presets  

## Visual Legend

The 3D view shows control hints:
```
🎮 Controls:
• Left Mouse: Rotate
• Right Mouse: Pan
• Wheel: Zoom
```

## Troubleshooting

### Pan doesn't work
- Make sure you're using the **right mouse button** (not left)
- Check that you're **dragging** (not just clicking)

### Can't add waypoints while panning
- This is correct behavior
- Left mouse = waypoints, Right mouse = pan

### View moves too fast/slow
- Pan speed automatically scales with zoom level
- Zoom in = slower, more precise panning
- Zoom out = faster panning

## What's Next?

- Explore your trajectories with ease
- Navigate complex flight paths
- Fine-tune waypoint placement with better visibility

## Need Help?

See full documentation: [PAN_CONTROL_FEATURE.md](PAN_CONTROL_FEATURE.md)

---

**Enjoy the enhanced 3D navigation! 🚁**
