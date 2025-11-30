# Quick Start: Auto Trajectory with Speed Control

## 🚀 Getting Started in 3 Steps

### Step 1: Run the Simulation
```bash
cd /workspace
python python/simulation.py
```

### Step 2: Create Waypoints with Speeds
1. **Check** ☑ "Click to Add Waypoints"
2. **Adjust** the "Waypoint Speed" slider (1-15 m/s)
3. **Click** on the 3D view to place waypoints
4. **Repeat** with different speeds for each waypoint

### Step 3: Watch It Fly!
1. **Click** "Generate Trajectory"
2. **Sit back** - The drone automatically starts and flies through all waypoints!
3. **Observe** how speed changes at each waypoint

## 📊 Quick Example

**Mission: Inspection Flight**

```
1. Set speed to 5 m/s, click to place WP1 at approach point
2. Set speed to 2 m/s, click to place WP2 at inspection point
3. Set speed to 3 m/s, click to place WP3 at second inspection point
4. Set speed to 8 m/s, click to place WP4 at return point
5. Click "Generate Trajectory"
6. Watch the drone automatically execute the mission!
```

**Result:** Drone flies slow during inspection, fast during transit - automatically!

## 🎛️ Key Controls

| Control | Location | Function |
|---------|----------|----------|
| **Waypoint Speed Slider** | Waypoint Manager | Set speed for next waypoint (1-15 m/s) |
| **Auto-Play Checkbox** | Waypoint Manager | Enable/disable auto-start (default: ON) |
| **Generate Trajectory** | Waypoint Manager | Create and start trajectory |
| **Dynamic Mode** | Waypoint Manager | Allow mid-flight changes |
| **Playback Speed** | Simulation Controls | Speed up/slow down visualization |

## ⚡ Quick Tips

1. **Higher speeds** for straight paths between waypoints
2. **Lower speeds** for precise operations or turns
3. **3m spacing minimum** between waypoints for smooth flight
4. **Auto-Play enabled** by default - no need to click Play!
5. **Target Speed** shown in Flight Telemetry panel

## 🎯 Common Scenarios

### Scenario 1: Fast Transit, Slow Inspection
```
WP1: (0, 0, 10) @ 10 m/s   → Fast takeoff
WP2: (20, 20, 15) @ 2 m/s  → Slow inspection
WP3: (40, 40, 10) @ 10 m/s → Fast return
```

### Scenario 2: Gradual Speed Changes
```
WP1: (10, 10, 10) @ 5 m/s  → Slow start
WP2: (20, 20, 12) @ 8 m/s  → Moderate
WP3: (30, 30, 15) @ 12 m/s → Fast cruise
```

### Scenario 3: Search Pattern
```
WP1: (10, 0, 10) @ 6 m/s
WP2: (10, 10, 10) @ 6 m/s
WP3: (20, 10, 10) @ 6 m/s  → Constant speed grid search
WP4: (20, 0, 10) @ 6 m/s
```

## 🔄 Dynamic Changes (Advanced)

Want to change the mission mid-flight?

1. ☑ Enable "Enable Dynamic Mode"
2. Add/remove waypoints while flying
3. Click "Apply Changes"
4. Drone automatically adjusts to new plan!

## 📈 What to Watch

- **Velocity display**: Shows current speed vs target speed
- **Waypoint indicator**: Shows which waypoint is current target
- **Target Speed field**: Shows the speed goal for current waypoint
- **Trail effect**: Enable to see flight path (optional)

## 🎮 Try This Now!

**5-Minute Challenge:**

1. Add 4 waypoints with speeds: 5, 10, 3, 8 m/s
2. Generate trajectory
3. Watch auto-play execute the mission
4. Enable "Show Trail Effect" to visualize path
5. Enable "Show Velocity Vector" to see direction
6. Try changing speeds mid-flight with Dynamic Mode!

## 💡 Pro Tips

- **Speed = Distance/Time**: Higher speeds mean faster mission completion
- **Smooth is fast**: Gradual speed changes are more efficient
- **Plan ahead**: Set appropriate speeds before generating
- **Test first**: Try different speeds to find optimal mission profile
- **Use playback speed**: Speed up visualization for testing, slow down for analysis

## 🆘 Need Help?

**Drone not moving?**
→ Check that "Auto-Play on Generate" is enabled (☑)

**Speed not changing?**
→ Verify speeds are set differently for each waypoint

**Want more control?**
→ Disable Auto-Play and use the Play button manually

**Want to change mid-flight?**
→ Enable "Dynamic Mode" and use "Apply Changes"

---

**That's it!** You're now ready to create dynamic, speed-controlled drone missions that execute automatically. Enjoy! ✈️

For more details, see [DYNAMIC_TRAJECTORY_GUIDE.md](DYNAMIC_TRAJECTORY_GUIDE.md)
