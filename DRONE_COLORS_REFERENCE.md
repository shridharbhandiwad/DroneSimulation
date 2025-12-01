# Drone Colors Quick Reference

## Color Values by Theme

### 🌙 BLACK THEME (Dark Background #1a1a1a)
**All parts use BRIGHT colors for visibility**

| Component | RGB Values | Description |
|-----------|------------|-------------|
| Hub (center) | `(0.7, 0.9, 1.0)` | Bright cyan |
| Top Plate | `(0.75, 0.85, 0.95)` | Bright silver-blue |
| Bottom Plate | `(0.70, 0.80, 0.92)` | Silver-blue |
| Arms (4x) | `(0.65, 0.75, 0.85)` | Bright gray-blue |
| Motors (4x) | `(0.70, 0.78, 0.88)` | Bright silver |
| Landing Gear (4x) | `(0.65, 0.72, 0.82)` | Bright gray |
| Propellers (12x) | `(0.60, 0.70, 0.85)` | Bright translucent |
| Gimbal | `(0.60, 0.68, 0.78)` | Bright gray |

**Visual Effect:** Bright, silvery drone that stands out clearly against dark background

---

### ☀️ WHITE THEME (Light Background #ffffff)
**All parts use DARK colors for contrast**

| Component | RGB Values | Description |
|-----------|------------|-------------|
| Hub (center) | `(0.20, 0.60, 0.86)` | Modern blue |
| Top Plate | `(0.15, 0.15, 0.18)` | Dark carbon fiber |
| Bottom Plate | `(0.12, 0.12, 0.15)` | Darker carbon |
| Arms (4x) | `(0.18, 0.18, 0.20)` | Dark gray |
| Motors (4x) | `(0.25, 0.25, 0.28)` | Medium gray |
| Landing Gear (4x) | `(0.15, 0.15, 0.17)` | Dark |
| Propellers (12x) | `(0.08, 0.08, 0.10)` | Very dark translucent |
| Gimbal | `(0.1, 0.1, 0.12)` | Very dark |

**Visual Effect:** Sleek, dark carbon fiber aesthetic that contrasts beautifully with light background

---

## Color Philosophy

### Design Principles
1. **High Contrast:** Colors are chosen to maximize visibility against their respective backgrounds
2. **Aesthetic Consistency:** 
   - Black theme = "Bright tech" look (silver/cyan metals)
   - White theme = "Carbon fiber" look (dark matte)
3. **Smooth Transitions:** All parts update simultaneously when switching themes
4. **RGB Range:** Black theme colors use values > 0.6, White theme uses values < 0.3

### Color Coordination
- **LED Accent Lights** (arms): Keep bright RGB colors in both themes
  - Front: Red
  - Back: Green
  - Right: Blue
  - Left: Yellow
- **Battery LEDs**: Always green (status indicator)
- **Antenna**: Always metallic silver (functional element)

## Before vs After

### ❌ BEFORE (Bug)
```
Black Theme Drone Colors:
- Hub: (0.20, 0.60, 0.86) ← Only part that was bright
- Top Plate: (0.15, 0.15, 0.18) ← DARK = INVISIBLE
- Arms: (0.18, 0.18, 0.20) ← DARK = INVISIBLE
- Motors: (0.25, 0.25, 0.28) ← DARK = INVISIBLE
- Everything else: DARK = INVISIBLE
```

**Problem:** Only the hub was visible; entire drone body disappeared into black background

### ✅ AFTER (Fixed)
```
Black Theme Drone Colors:
- Hub: (0.7, 0.9, 1.0) ← BRIGHT
- Top Plate: (0.75, 0.85, 0.95) ← BRIGHT
- Arms: (0.65, 0.75, 0.85) ← BRIGHT
- Motors: (0.70, 0.78, 0.88) ← BRIGHT
- Everything: BRIGHT = VISIBLE
```

**Result:** Entire drone is clearly visible with beautiful silver-blue appearance

## Code Location
All color definitions are in: `python/simulation.py`
- Method: `apply_theme_to_3d_scene()`
- Lines: ~1471-1598
- Theme check: `if self.current_theme == 'white'` vs `else:` (black theme)
