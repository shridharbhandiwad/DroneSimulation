# 🚁 Drone Simulation - Quick Reference Card

## 🏃 Launch
```bash
cd /workspace && python3 python/simulation.py
```

## 🎮 Essential Controls

### Adding Waypoints
1. ☑️ Check "Click to Add Waypoints"
2. 🎚️ Set height: 5-30m (default: 10m)
3. 🖱️ Click in 3D view
4. ✨ Click "Generate Trajectory"
5. ▶️ Click "Play"

### Simulation Control
| Button | Action |
|--------|--------|
| ▶️ Play | Start simulation |
| ⏸️ Pause | Pause simulation |
| 🔄 Reset | Return to start |
| 🎲 Random | Generate random path |

### Waypoint Management
| Button | Action |
|--------|--------|
| ➖ Remove | Delete selected |
| 🗑️ Clear All | Delete all |
| ✨ Generate | Create trajectory |

## 🎨 Visual Guide

### Markers
- 🔴 Red (15px): Drone position
- 🔵 Blue (12px): Trajectory waypoints
- 🟡 Gold (14px): User waypoints
- 🟢 Green line: Flight path

### Button Colors
- 🟢 Green: Play/Pause
- 🔵 Blue: Standard actions
- 🟠 Orange: Reset/clear
- 🟣 Purple: Random
- 🔷 Teal: Generate

## 🖱️ Mouse Controls

| Action | Control |
|--------|---------|
| Rotate view | Left drag |
| Pan view | Right drag |
| Zoom | Scroll wheel |
| Add waypoint* | Click |

*When click mode is enabled

## ⚙️ Speed Settings

| Speed | Use Case |
|-------|----------|
| 0.1x - 0.5x | Slow motion study |
| 1.0x | Real-time |
| 2.0x - 3.0x | Quick preview |
| 4.0x - 5.0x | Rapid testing |

## 📊 Status Messages

| Message | Meaning |
|---------|---------|
| "Click mode enabled" | Can add waypoints |
| "Added waypoint at..." | Waypoint added |
| "Generated trajectory..." | Path created |
| "Simulation playing" | Running |
| "Simulation complete" | Finished |

## 💡 Quick Tips

1. **Start with 3-4 waypoints** for smooth paths
2. **Use 10-15m height** for best visibility
3. **Preview at 0.5x speed** for first run
4. **Zoom out** to see full trajectory
5. **Status bar** shows helpful messages

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| Can't add waypoints | Check click mode box |
| Waypoints too high/low | Adjust height slider |
| Trajectory too fast | Lower speed slider |
| Can't see path | Zoom out with scroll |

## 📁 Documentation

| File | Purpose |
|------|---------|
| `USER_GUIDE.md` | Complete manual |
| `FEATURE_UPDATE.md` | New features |
| `MODIFICATIONS_SUMMARY.md` | What changed |
| `QUICK_REFERENCE.md` | This file |

## 🎯 Common Workflows

### Quick Test
```
1. Click "🎲 Random Trajectory"
2. Set speed to 2.0x
3. Click "▶️ Play"
```

### Custom Path
```
1. Check "Click to Add Waypoints"
2. Click 3-5 positions
3. Click "✨ Generate Trajectory"
4. Click "▶️ Play"
```

### Refine Path
```
1. Select waypoint in list
2. Click "➖ Remove"
3. Add new waypoint
4. Click "✨ Generate Trajectory"
```

## 📐 Layout

```
┌────────────────────────────────────┐
│  [3D View]  [Controls]  [Camera]  │
│     Big       Middle      Right   │
│   800x550    Panels     640x480   │
└────────────────────────────────────┘
```

## ⌨️ No Keyboard Shortcuts
All controls are mouse/UI based

## 🎓 Learning Path

1. Try random trajectory (30 seconds)
2. Add 3 waypoints manually (2 minutes)
3. Generate and play (1 minute)
4. Experiment with heights (5 minutes)
5. Create complex patterns (10 minutes)

## 📊 Telemetry Display

```
Position:     Current X, Y, Z
Velocity:     Speed in m/s
Acceleration: Rate of change
Current WP:   Target waypoint
Time:         Elapsed seconds
Progress:     % complete
```

## 🌐 Window Size
**Recommended**: 1600x900 or larger

## 🔧 Dependencies
✅ All installed automatically

## ⚡ Performance
- 60 FPS rendering
- Real-time updates
- No lag

---

**Print this for quick access! 📄**

*Version 2.0 - Enhanced Edition*
