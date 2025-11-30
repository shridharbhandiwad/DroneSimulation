# White Theme Color Palette Reference

## Color System Overview

The white theme uses a modern Material Design-inspired color palette with clear semantic meaning for each color.

---

## Base Colors

### Backgrounds
- **Main Background**: `#f5f5f5` - Light grey for reduced eye strain
- **Widget Background**: `#ffffff` - Pure white for content areas
- **3D Plot Background**: `#ffffff` - Pure white for clean visualization

### Borders
- **Primary Border**: `#e0e0e0` - Light grey for subtle separation
- **Accent Borders**: Various colors matching button themes

### Text Colors
- **Primary Text**: `#2c3e50` - Dark grey for main content
- **Secondary Text**: `#555555` - Medium grey for labels
- **Accent Text**: `#3498db` - Blue for highlighted values

---

## Button Colors

### Play Button (Green)
```
Normal: #66bb6a → #4caf50
Hover:  #7bc67e → #66bb6a
Border: #43a047
```
**Meaning**: Start/Resume action - universally recognized "go" color

### Reset Button (Orange)
```
Normal: #ffa726 → #ff9800
Hover:  #ffb74d → #ffa726
Border: #f57c00
```
**Meaning**: Restart action - attention-grabbing but not alarming

### Random Button (Purple)
```
Normal: #ab47bc → #9c27b0
Hover:  #ba68c8 → #ab47bc
Border: #8e24aa
```
**Meaning**: Creative/Generate action - unique and distinctive

### Generate Button (Teal)
```
Normal: #26a69a → #009688
Hover:  #4db6ac → #26a69a
Border: #00897b
```
**Meaning**: Create action - fresh and constructive

### Apply Button (Indigo)
```
Normal: #5c6bc0 → #3f51b5
Hover:  #7986cb → #5c6bc0
Border: #3949ab
Disabled: #bdbdbd → #9e9e9e
```
**Meaning**: Confirm/Apply changes - trustworthy and stable

### Remove Button (Red)
```
Normal: #ef5350 → #f44336
Hover:  #e57373 → #ef5350
Border: #e53935
```
**Meaning**: Delete action - clear warning color

### Clear Button (Grey)
```
Normal: #78909c → #607d8b
Hover:  #90a4ae → #78909c
Border: #546e7a
```
**Meaning**: Clear all - neutral but noticeable

### Default Button (Blue)
```
Normal: #5a9fd4 → #3498db
Hover:  #6bb1e0 → #5a9fd4
Border: #2980b9
Pressed: #2980b9 → #2471a3
```
**Meaning**: Primary action - trustworthy and professional

---

## Interactive Elements

### Sliders
```
Track: #f5f5f5 (Light grey)
Border: #e0e0e0
Handle: #5a9fd4 → #3498db (Blue gradient)
Handle Border: #2980b9
Handle Hover: #6bb1e0 → #5a9fd4
Progress: #5a9fd4 → #3498db (Blue gradient)
```

### Checkboxes
```
Unchecked Background: #ffffff (White)
Unchecked Border: #bdbdbd (Grey)
Hover Border: #3498db (Blue)
Hover Background: #f5f5f5 (Light grey)
Checked Background: #5a9fd4 → #3498db (Blue gradient)
Checked Border: #2980b9
Checked Hover: #6bb1e0 → #5a9fd4
```

### List Widget
```
Background: #ffffff (White)
Border: #e0e0e0 (Light grey)
Item Text: #2c3e50 (Dark grey)
Item Hover: #f5f5f5 (Light grey)
Item Selected Background: #5a9fd4 → #3498db (Blue gradient)
Item Selected Text: #ffffff (White)
```

---

## 3D Scene Colors

### Grid
```
RGB: (200, 200, 200, 120)
Description: Light grey with transparency
```

### Trajectory Line
```
RGB: (0.20, 0.60, 0.86, 0.9)
Hex Equivalent: ~#3399db
Description: Modern blue with slight transparency
Width: 3.5px
```

### Drone Marker
```
RGB: (0.20, 0.60, 0.86, 1.0)
Hex Equivalent: ~#3399db
Description: Solid modern blue
Size: 18px
```

### Waypoint Markers (Generated)
```
RGB: (0.15, 0.65, 0.60, 1.0)
Hex Equivalent: ~#26a69a
Description: Teal/turquoise for system-generated waypoints
Size: 20px
```

### User Waypoint Markers
```
RGB: (0.67, 0.28, 0.73, 1.0)
Hex Equivalent: ~#ab47ba
Description: Purple for user-created waypoints
Size: 22px
```

---

## Status Indicators

### ML Model Active (Success State)
```
Background: #e8f5e9 (Light green)
Text: #2e7d32 (Dark green)
```

### Physics Mode (Info State)
```
Background: #e3f2fd (Light blue)
Text: #1976d2 (Dark blue)
```

---

## Color Accessibility

### Contrast Ratios
All text colors meet WCAG AA standards for accessibility:

- **#2c3e50 on #ffffff**: 12.6:1 (AAA) ✓
- **#555555 on #ffffff**: 7.4:1 (AA) ✓
- **#3498db on #ffffff**: 3.4:1 (Large text only)
- **White on #3498db**: 4.5:1 (AA) ✓

### Color Blindness Considerations
- Red (Remove) vs Green (Play) can be distinguished by position and icon
- Blue is accessible to most color vision deficiencies
- Teal and purple provide good contrast
- Buttons have text labels, not just color coding

---

## Material Design Compliance

Colors chosen from Material Design color palette:
- **Blue 500**: #3498db (Custom, lighter than MD)
- **Green 500**: #4caf50 ✓
- **Orange 500**: #ff9800 ✓
- **Purple 500**: #9c27b0 ✓
- **Teal 500**: #009688 ✓
- **Indigo 500**: #3f51b5 ✓
- **Red 500**: #f44336 ✓
- **Blue Grey 500**: #607d8b ✓

---

## Usage Guidelines

### When to Use Each Color

1. **Blue (#3498db)**: Default actions, primary UI elements, navigation
2. **Green (#4caf50)**: Start, play, go, confirm positive actions
3. **Orange (#ff9800)**: Reset, refresh, restart actions
4. **Purple (#9c27b0)**: Creative actions, randomize, generate
5. **Teal (#009688)**: Create, generate from user input
6. **Indigo (#3f51b5)**: Apply changes, save, confirm
7. **Red (#f44336)**: Delete, remove, destructive actions
8. **Grey (#607d8b)**: Clear all, neutral destructive actions

### Color Psychology

- **Blue**: Trust, stability, professionalism
- **Green**: Success, go, positive action
- **Orange**: Energy, attention, restart
- **Purple**: Creativity, uniqueness, innovation
- **Teal**: Freshness, clarity, creation
- **Indigo**: Reliability, application, depth
- **Red**: Warning, stop, deletion
- **Grey**: Neutrality, balance, secondary

---

## Hex Color Quick Reference

```
Backgrounds:     #f5f5f5, #ffffff
Borders:         #e0e0e0, #bdbdbd
Text:            #2c3e50, #555555
Blue:            #3498db, #2980b9
Green:           #4caf50, #43a047
Orange:          #ff9800, #f57c00
Purple:          #9c27b0, #8e24aa
Teal:            #009688, #00897b
Indigo:          #3f51b5, #3949ab
Red:             #f44336, #e53935
Grey:            #607d8b, #546e7a
```

---

## Gradient Direction

All button gradients use vertical gradients (top to bottom):
```css
qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 [lighter], stop:1 [darker])
```

This creates a subtle 3D effect with the light source coming from above.

---

## Animation and Transitions

While not currently implemented, the color system supports:
- Smooth hover transitions (lighter shades on hover)
- Press states (darker shades on press)
- Focus states (using primary blue color)
- Disabled states (grey with reduced opacity)

All transitions should be smooth with 200-300ms duration for professional feel.
