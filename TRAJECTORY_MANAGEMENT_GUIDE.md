# Trajectory Save/Load and Templates Guide

## Overview

The Drone Trajectory Simulation system now includes powerful trajectory management features:

1. **Save/Load Trajectories** - Save your custom trajectories and reload them later
2. **Pre-defined Templates** - 13 ready-to-use trajectory patterns
3. **Trajectory Browser** - Browse, load, and manage saved trajectories

## Features

### 1. Save Current Trajectory

Save your current waypoints to a file for later use.

**How to use:**
- Menu: `File → Trajectory → 💾 Save Trajectory...` (Ctrl+S)
- Button: Click `💾 Save` in Waypoint Manager panel
- Enter a name and optional description
- Trajectories are saved as JSON files in `saved_trajectories/` folder

**What gets saved:**
- All waypoint positions (x, y, z)
- Speed for each waypoint
- Trajectory name and description
- Creation timestamp
- Optional metadata

### 2. Load Saved Trajectories

Browse and load previously saved trajectories.

**How to use:**
- Menu: `File → Trajectory → 📂 Browse Trajectories...` (Ctrl+O)
- Button: Click `📂 Load` in Waypoint Manager panel
- Browse the list of saved trajectories
- Double-click or select and click "Load"
- The waypoints will be loaded and displayed

**Browser features:**
- View all saved trajectories in a table
- See waypoint count, creation date, and description
- Delete unwanted trajectories
- Refresh the list
- Sort by date (newest first)

### 3. Pre-defined Templates

Choose from 13 professionally designed trajectory patterns.

**How to use:**
- Menu: `File → Trajectory → ✨ Load Template...` (Ctrl+T)
- Button: Click `✨ Load Template` in Waypoint Manager panel
- Select a template from the list
- Customize parameters (center position, size, speed, waypoint count)
- Click OK to load

## Available Templates

### Basic Patterns

#### 1. **Circle**
- Circular trajectory around a center point
- Perfect for orbit patterns and surveillance
- Parameters: radius, center position, speed

#### 2. **Square**
- Rectangular path with four corners
- Tests sharp direction changes
- Parameters: side length, center position, speed

### Vertical Maneuvers

#### 3. **Ascend**
- Straight vertical climb
- Quick altitude gain
- Parameters: start position, height change, speed

#### 4. **Descend**
- Controlled vertical descent
- Smooth landing approach
- Parameters: start position, height change, speed

### Spiral Patterns

#### 5. **Spiral (Ascending)**
- Upward spiral increasing in radius and altitude
- Great for gaining height while moving outward
- Parameters: start/end radius, start/end height, rotation count

#### 6. **Spiral (Descending)**
- Downward spiral decreasing in radius and altitude
- Useful for controlled descent patterns
- Parameters: start/end radius, start/end height, rotation count

### Turn Maneuvers

#### 7. **Sharp Turn (Right)**
- L-shaped path with 90° right turn
- Tests drone agility
- Parameters: leg length, turn point

#### 8. **Sharp Turn (Left)**
- L-shaped path with 90° left turn
- Aggressive direction change
- Parameters: leg length, turn point

### Curve Patterns

#### 9. **S-Curve (Horizontal)**
- Sinusoidal wave pattern in horizontal plane
- Tests smooth lateral control
- Parameters: length, amplitude, wave count

#### 10. **S-Curve (Vertical)**
- Sinusoidal wave with vertical oscillations
- Altitude-varying path
- Parameters: length, amplitude, wave count

#### 11. **C-Curve (Horizontal)**
- Partial circular arc (C-shape) in horizontal plane
- Smooth curved approach
- Parameters: radius, arc angle

#### 12. **C-Curve (Vertical)**
- Partial circular arc in vertical plane
- Vertical curved maneuver
- Parameters: radius, arc angle

### Advanced Patterns

#### 13. **Figure-Eight**
- Figure-eight (∞) pattern
- Complex trajectory for precision testing
- Parameters: center, radius, plane (horizontal/vertical)

## Template Parameters

All templates support these common parameters:

- **Center/Start Position** - X, Y, Z coordinates in meters
- **Size/Radius** - Overall size of the pattern in meters
- **Speed** - Flight speed in m/s
- **Number of Waypoints** - Density of waypoints along path

## File Format

Trajectories are saved as JSON files with this structure:

```json
{
  "name": "My Trajectory",
  "description": "Custom flight path",
  "created_at": "2025-12-01T10:30:00",
  "waypoints": [
    {
      "position": [10.0, 5.0, 15.0],
      "speed": 12.0
    },
    ...
  ],
  "metadata": {}
}
```

## Storage Location

Saved trajectories are stored in:
```
/workspace/saved_trajectories/
```

Each file is named with the format:
```
<trajectory_name>_<timestamp>.json
```

## Usage Tips

### Creating Complex Patterns

1. Load a template as a base
2. Add custom waypoints using click-to-add mode
3. Modify speeds as needed
4. Save for later use

### Combining Templates

1. Load first template
2. Note the end position
3. Load second template with adjusted start position
4. Save the combined trajectory

### Trajectory Libraries

Organize your trajectories by purpose:
- **Test patterns** - For validating drone behavior
- **Inspection routes** - For infrastructure monitoring
- **Survey patterns** - For area coverage
- **Performance tests** - For speed and agility testing

## Keyboard Shortcuts

- `Ctrl+S` - Save current trajectory
- `Ctrl+O` - Browse saved trajectories
- `Ctrl+T` - Load template

## Export Options

Trajectories can also be exported to:
- **CSV format** - For data analysis
- **Training data** - For ML model training
- **ONNX format** - For C++ integration

## Troubleshooting

### Trajectory won't save
- Ensure you have added waypoints first
- Check that you have write permissions to `saved_trajectories/` folder

### Can't find saved trajectory
- Click "Refresh" button in browser
- Check the `saved_trajectories/` folder exists

### Template generates unexpected path
- Review parameter values (especially center position)
- Try default parameters first
- Check waypoint count (higher = smoother)

## API Usage

### Programmatic Access

```python
from trajectory_storage import TrajectoryStorage
from trajectory_templates import TrajectoryTemplates

# Create storage instance
storage = TrajectoryStorage()

# Generate template
waypoints = TrajectoryTemplates.circle(
    center=(0, 0, 15),
    radius=20,
    speed=12,
    num_points=20
)

# Save trajectory
filepath = storage.save_trajectory(
    waypoints,
    "My Circle",
    "A circular trajectory for testing"
)

# Load trajectory
loaded = storage.load_trajectory(filepath)

# List all trajectories
all_trajectories = storage.list_trajectories()
```

### Available Template Methods

```python
# Basic patterns
TrajectoryTemplates.circle(...)
TrajectoryTemplates.square(...)

# Vertical maneuvers
TrajectoryTemplates.ascend(...)
TrajectoryTemplates.descend(...)

# Spirals
TrajectoryTemplates.spiral(..., ascending=True)
TrajectoryTemplates.spiral(..., ascending=False)

# Turns
TrajectoryTemplates.sharp_turn(..., direction='right')
TrajectoryTemplates.sharp_turn(..., direction='left')

# Curves
TrajectoryTemplates.s_curve(..., axis='xy')  # horizontal
TrajectoryTemplates.s_curve(..., axis='xz')  # vertical
TrajectoryTemplates.c_curve(..., plane='xy')  # horizontal
TrajectoryTemplates.c_curve(..., plane='xz')  # vertical

# Advanced
TrajectoryTemplates.figure_eight(...)

# Get template by name
waypoints = TrajectoryTemplates.get_template('circle', radius=20, speed=12)

# List all available templates
templates = TrajectoryTemplates.get_template_list()
```

## Integration with Existing Features

The new trajectory management integrates seamlessly with:

- **Dynamic Waypoint Mode** - Load a template, then modify waypoints in real-time
- **Auto-Play** - Automatically starts simulation when loading templates/trajectories
- **Theme Support** - All dialogs respect current theme (white/black)
- **Follow Drone Mode** - Camera tracks drone through loaded trajectories
- **Velocity Vectors** - Visual feedback on template-generated paths

## Version History

### Version 2.1
- ✨ Added trajectory save/load functionality
- ✨ Added 13 pre-defined trajectory templates
- ✨ Added trajectory browser with table view
- ✨ Added template parameter customization
- 🎨 Added save/load buttons to Waypoint Manager
- 🎨 Added File → Trajectory menu
- 📝 Updated keyboard shortcuts

## Next Steps

After loading or creating trajectories, you can:

1. **Simulate** - Click Play to watch the drone follow the path
2. **Modify** - Use dynamic waypoint mode to adjust in real-time
3. **Export** - Save as training data or export to ONNX
4. **Share** - JSON files can be shared with team members

## Support

For issues or questions:
- See main README.md
- Check existing documentation files
- Review trajectory_templates.py for template implementation
- Review trajectory_storage.py for storage implementation

---

**Enjoy creating and managing your drone trajectories! 🚁✨**
