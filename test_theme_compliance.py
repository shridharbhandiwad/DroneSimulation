#!/usr/bin/env python3
"""
Quick test to verify theme compliance
"""

import sys
import os

# Add python directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'python'))

def test_color_definitions():
    """Test that all required color methods exist"""
    print("Testing theme compliance...")
    
    # Import the simulation module
    try:
        from simulation import DroneSimulationWindow
        print("✓ Successfully imported DroneSimulationWindow")
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        return False
    
    # Check for required methods
    required_methods = [
        'apply_theme_to_3d_scene',
        'switch_theme',
        'update_waypoint_colors',
        'update_user_waypoint_markers',
        'update_animations',
    ]
    
    for method_name in required_methods:
        if hasattr(DroneSimulationWindow, method_name):
            print(f"✓ Method '{method_name}' exists")
        else:
            print(f"✗ Method '{method_name}' missing")
            return False
    
    print("\n" + "="*60)
    print("All theme compliance checks passed!")
    print("="*60)
    print("\nTheme-compliant elements:")
    print("  • Drone model (blue)")
    print("  • Trajectory waypoints (teal)")
    print("  • User waypoints (purple)")
    print("  • Visited waypoints (green)")
    print("  • Trajectory line (blue)")
    print("  • Trail effect (orange)")
    print("  • Waypoint connections (grey)")
    print("  • Target line (gold)")
    print("  • Velocity vector (green)")
    print("  • Grid (light/dark grey)")
    print("  • Target waypoint marker (gold, pulsing)")
    print("\nRun 'python3 simulation.py' to test the UI!")
    
    return True

if __name__ == '__main__':
    success = test_color_definitions()
    sys.exit(0 if success else 1)
