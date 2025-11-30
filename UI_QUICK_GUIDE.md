# 3D Trajectory View - Quick Reference Guide

## 🚀 Quick Start

```bash
cd /workspace
python3 python/simulation.py
```

---

## 🎮 Controls At A Glance

### Camera Views (Click Buttons)
```
⬆ Top       - Bird's eye view
↔ Side      - Side perspective
⬌ Front     - Front perspective  
🔲 Isometric - 3D default view
```

### Visual Toggles (Checkboxes)
```
✓ Show Trail Effect          - Orange trail behind drone
✓ Show Velocity Vector       - Green direction arrow
✓ Show Waypoint Connections  - Teal lines between waypoints
✓ Show Target Line          - Golden line to target
☐ Follow Drone              - Camera tracks drone
```

### Mouse Controls
```
Left Click + Drag   → Rotate view
Right Click + Drag  → Pan view
Scroll Wheel        → Zoom in/out
```

---

## 🎨 Color Guide

```
🔵 Blue    - Drone position
🟢 Teal    - Trajectory waypoints
🟣 Purple  - User waypoints
🟡 Gold    - Current target (pulsing!)
🟠 Orange  - Trail effect
🟢 Green   - Velocity vector
🔴 Red     - X-axis
🟢 Green   - Y-axis
🔵 Blue    - Z-axis
```

---

## 📊 Information Display

### Flight Telemetry Panel
```
Position      : (x, y, z) coordinates
Velocity      : Speed | (vx, vy, vz)
Acceleration  : (ax, ay, az)
Current WP    : #N | Distance
Time          : Elapsed seconds
Progress      : Step count and %
```

---

## 💡 Pro Tips

### Best Views for Different Tasks
- **Path Planning**: Use **Top View** (⬆)
- **Altitude Check**: Use **Side View** (↔)
- **General Use**: Use **Isometric** (🔲)
- **Following Drone**: Enable **Follow Drone** checkbox

### Visual Clarity
- Disable **Trail** if path is too cluttered
- Disable **Velocity Vector** when paused
- Disable **Target Line** for cleaner look
- Enable **Follow Mode** for demo/presentation

### Navigation
- Use **Right Click + Drag** to center view
- Use **Scroll** to zoom to perfect distance
- Use **Preset Views** to reset orientation

---

## 🎯 What Each Visual Element Shows

### Trajectory Line (Blue)
- Complete planned path
- Shows full route from start to finish

### Trail (Orange, Thick)
- Last 20 drone positions
- Shows recent flight path
- Updates in real-time

### Velocity Vector (Green Arrow)
- Current speed direction
- Arrow length = speed magnitude
- Scaled 3x for visibility

### Target Line (Golden Yellow)
- Connects drone to current waypoint
- Shows immediate navigation goal
- Semi-transparent

### Waypoint Connections (Teal Dotted)
- Links all waypoints in sequence
- Shows planned route order
- Helpful for path understanding

### Markers
- **Drone** (Blue + Glow): Current position
- **Waypoints** (Teal + Glow): Trajectory points
- **User Waypoints** (Purple + Glow): Custom points
- **Target** (Gold, Pulsing): Current goal

---

## ⚡ Keyboard Shortcuts

Currently mouse-based, but buttons provide quick access:
- **Play/Pause**: Toggle simulation
- **Reset**: Return to start
- **Random**: Generate new trajectory
- **Camera Buttons**: Instant view changes

---

## 🎬 Demo Sequence

Perfect sequence for demonstrations:

1. **Start** - Default Isometric view
2. **Generate** - Click "🎲 Random" for new trajectory
3. **Play** - Click "▶ Play" to start
4. **Follow** - Enable "Follow Drone"
5. **Views** - Cycle through camera presets
6. **Pause** - Click "⏸ Pause" to examine
7. **Reset** - Click "⟲ Reset" when done

---

## 🔍 Troubleshooting

### Can't see drone?
- Click **⟲ Reset** to return to start
- Use **Scroll** to zoom out
- Try **Follow Drone** mode

### View is rotated wrong?
- Click any **Camera Preset** button
- Use **🔲 Isometric** for default

### Too many lines?
- Uncheck visual options you don't need
- Disable **Trail** for cleaner view
- Disable **Target Line** to reduce clutter

### Performance issues?
- Disable **Trail Effect**
- Reduce window size
- Close other applications

---

## 📏 Grid Reference

### Grid Spacing
- **Minor Grid** (Light): 1 meter
- **Major Grid** (Darker): 5 meters

### Axes
- **Red Line**: X-axis (extends 50m)
- **Green Line**: Y-axis (extends 50m)
- **Blue Line**: Z-axis (extends 50m upward)

---

## 🎨 Legend (On-Screen)

Look for the semi-transparent box in the **top-left corner** showing:
- All color codes
- Mouse controls
- Quick reference

*Legend is mouse-transparent - it won't block your interactions!*

---

## 💾 Default Settings

When you first start:
```
✓ Trail Effect         - ON
✓ Velocity Vector      - ON
✓ Waypoint Connections - ON
✓ Target Line         - ON
☐ Follow Drone        - OFF

Camera: Isometric view
Distance: 100 units
Speed: 1.0x
```

---

## 📐 Measurement Tips

### Distance Estimation
- Use **grid squares** (1m or 5m)
- Check **"Dist: Xm"** in Current WP info
- Use **position coordinates**

### Speed Estimation
- Check **velocity display** (shows m/s)
- Watch **velocity arrow** length
- Monitor **position change rate**

### Height Check
- Look at **Z coordinate** in position
- Compare to **grid plane** (ground = 0)
- Use **side view** for profile

---

## 🎓 Advanced Usage

### Multiple Waypoints
1. Enable "Click to Add Waypoints"
2. Set desired height with slider
3. Click on 3D view to add points
4. Click "Generate Trajectory"

### Dynamic Changes
1. Generate initial trajectory
2. Enable "Enable Dynamic Mode"
3. Add/modify waypoints during flight
4. Click "Apply Changes"

### Custom View
1. Use mouse to find perfect angle
2. Adjust zoom with scroll
3. Pan to center subject
4. *(Save view feature coming soon)*

---

## 📞 Need Help?

Check these files:
- **`UI_3D_IMPROVEMENTS.md`** - Full technical docs
- **`UI_IMPROVEMENTS_SUMMARY.md`** - Feature overview
- **`README.md`** - Project documentation

---

## ✨ Feature Highlights

**Most Useful:**
1. ✓ Velocity Vector - See speed/direction
2. ✓ Target Line - Know where heading
3. ✓ Camera Presets - Quick perfect views
4. ✓ Follow Mode - Auto tracking
5. ✓ Trail Effect - See path history

**Most Beautiful:**
1. ✓ Pulsing Target - Animated goal
2. ✓ Glow Effects - Marker halos
3. ✓ Color Scheme - Professional palette
4. ✓ Smooth Lines - Antialiased rendering
5. ✓ Legend Overlay - Clean information

---

## 🎯 Best Practices

### For Analysis
- Use **Side View** for altitude analysis
- Enable all visual elements
- Disable **Follow Mode** to pan freely

### For Presentation
- Use **Follow Mode** for dynamic shots
- Keep all visual elements on
- Use **Isometric** view for best angle

### For Debugging
- **Velocity Vector** shows motion issues
- **Target Line** shows navigation
- **Trail** shows actual vs planned path

---

**Enjoy your enhanced 3D trajectory visualization! 🚁✨**
