# Quick Start: Trajectory Save/Load & Templates

## New Features in Version 2.1 🎉

Three powerful new features for managing drone trajectories:

1. **💾 Save Trajectories** - Save your waypoints to files
2. **📂 Load Trajectories** - Browse and reopen saved trajectories  
3. **✨ Templates** - 13 pre-made trajectory patterns

---

## 60-Second Quick Start

### Use a Template

1. Run simulation: `python3 simulation.py` (or `python simulation.py` on Windows)
2. Click **✨ Load Template** button (or press `Ctrl+T`)
3. Select a pattern (e.g., "Circle")
4. Adjust parameters if needed
5. Click **OK**
6. Trajectory appears and starts playing! 🚁

### Save Your Work

1. Create waypoints (click-to-add or templates)
2. Click **💾 Save** button (or press `Ctrl+S`)
3. Enter a name
4. Done! Your trajectory is saved

### Load Saved Trajectory

1. Click **📂 Load** button (or press `Ctrl+O`)
2. Browse your saved trajectories
3. Double-click one to load it
4. Trajectory appears and starts playing! 🚁

---

## Available Templates

### 🔵 Basic Patterns
- **Circle** - Orbit around a point
- **Square** - Rectangular path with corners
- **Figure-Eight** - ∞ pattern

### ⬆️ Vertical Moves
- **Ascend** - Climb vertically
- **Descend** - Descend vertically

### 🌀 Spirals
- **Spiral (Ascending)** - Rise in a spiral
- **Spiral (Descending)** - Descend in a spiral

### ↩️ Turns
- **Sharp Turn (Right)** - 90° right turn
- **Sharp Turn (Left)** - 90° left turn

### 〰️ Curves
- **S-Curve (Horizontal)** - Wave pattern
- **S-Curve (Vertical)** - Vertical wave
- **C-Curve (Horizontal)** - Arc path
- **C-Curve (Vertical)** - Vertical arc

---

## UI Locations

### Menu Bar
```
File → Trajectory
  ├── 💾 Save Trajectory...     (Ctrl+S)
  ├── 📂 Browse Trajectories... (Ctrl+O)
  └── ✨ Load Template...       (Ctrl+T)
```

### Waypoint Manager Panel
```
[Waypoint List]

[Remove] [Clear All]

[✨ Load Template]    ← Load pre-made patterns
[💾 Save] [📂 Load]  ← Save/Load your trajectories

[Generate Trajectory]
```

---

## Typical Workflows

### Quick Test Flight
```
1. Ctrl+T (Load Template)
2. Select "Circle"
3. Click OK
4. Watch it fly! ▶
```

### Create & Save Custom Pattern
```
1. Enable "Click to Add Waypoints"
2. Click on 3D view to add points
3. Ctrl+S (Save)
4. Enter name: "My Pattern"
5. Done!
```

### Reuse Saved Work
```
1. Ctrl+O (Browse)
2. Double-click "My Pattern"
3. Modify if needed
4. Play! ▶
```

### Combine Template + Custom
```
1. Ctrl+T → Load "S-Curve"
2. Enable "Click to Add"
3. Add more waypoints
4. Ctrl+S → Save as "Custom Flight"
```

---

## File Storage

Trajectories are saved in:
```
/workspace/saved_trajectories/
```

Format: JSON (human-readable, shareable)

Example filename:
```
My_Circle_Pattern_20251201_143022.json
```

---

## Tips & Tricks

### 💡 Adjust Template Parameters
- **Center Position** - Where the pattern starts
- **Size/Radius** - How big the pattern is
- **Speed** - Flight speed (m/s)
- **Waypoints** - More = smoother path

### 💡 Auto-Play
Check "Auto-Play on Generate" to automatically start simulation when loading templates/trajectories

### 💡 Dynamic Editing
1. Load template
2. Enable "🔄 Dynamic Waypoint Mode"
3. Add/modify waypoints during flight!
4. Click "⚡ Apply Waypoint Changes"

### 💡 Combining Patterns
1. Load first template
2. Note end position
3. Create second pattern starting there
4. Save combined result

### 💡 Export Options
Saved trajectories can be:
- Loaded in simulation
- Used for training data
- Exported to CSV
- Shared with team

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+T` | Load Template |
| `Ctrl+S` | Save Trajectory |
| `Ctrl+O` | Browse/Load Trajectories |
| `Ctrl+,` | Open Settings |
| `Space` | Play/Pause |

---

## Troubleshooting

### "No waypoints to save"
→ Add waypoints first (click-to-add or load template)

### Can't see saved trajectories
→ Click "Refresh" in browser dialog

### Template doesn't look right
→ Try adjusting center position and size parameters

### Waypoints appear but trajectory doesn't generate
→ Click "Generate Trajectory" button or enable "Auto-Play"

---

## What's Next?

After loading/creating trajectories:

1. **🎮 Simulate** - Watch the drone fly
2. **🎨 Customize** - Adjust waypoint speeds
3. **🔄 Modify** - Use dynamic waypoint mode
4. **💾 Save** - Keep it for later
5. **📤 Export** - Use for training/analysis

---

## Examples in Action

### Example 1: Quick Surveillance Pattern
```
Ctrl+T → "Circle" → Radius: 30m → Speed: 10 m/s → OK
Result: Drone orbits at 30m radius
```

### Example 2: Inspection Route
```
Ctrl+T → "Square" → Side: 40m → OK
Add custom waypoints at inspection points
Ctrl+S → "Building Inspection Route"
```

### Example 3: Altitude Test
```
Ctrl+T → "Spiral (Ascending)" → End Height: 50m → OK
Result: Drone climbs in expanding spiral to 50m
```

---

## For Developers

See `TRAJECTORY_MANAGEMENT_GUIDE.md` for:
- API documentation
- File format specification
- Programmatic usage
- Custom template creation

---

## Version Info

- **Version**: 2.1
- **New Files**:
  - `python/trajectory_templates.py` - Template library
  - `python/trajectory_storage.py` - Save/load system
  - `python/test_trajectory_features.py` - Test suite
- **Modified Files**:
  - `python/simulation.py` - Added UI integration

---

**Ready to fly? 🚁 Press `Ctrl+T` and get started!**

For detailed documentation, see:
- `TRAJECTORY_MANAGEMENT_GUIDE.md` - Complete guide
- `README.md` - Main documentation
- `python/test_trajectory_features.py` - Run tests
