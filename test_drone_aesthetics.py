#!/usr/bin/env python3
"""
Test script to verify the improved drone aesthetics.
This script checks that all new drone model components are properly initialized.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

import numpy as np
from PyQt5.QtWidgets import QApplication
from simulation import DroneSimulationWindow

def test_drone_model_components():
    """Test that all drone model components are properly created"""
    print("Testing improved drone model aesthetics...")
    
    app = QApplication(sys.argv)
    window = DroneSimulationWindow()
    
    # Check body components
    assert hasattr(window, 'drone_body_top'), "Missing top body plate"
    assert hasattr(window, 'drone_body_bottom'), "Missing bottom body plate"
    assert hasattr(window, 'drone_hub'), "Missing central hub"
    print("✓ Body components created")
    
    # Check arms and motors
    assert hasattr(window, 'drone_arms'), "Missing drone arms"
    assert len(window.drone_arms) == 4, "Should have 4 arms"
    assert hasattr(window, 'motor_housings'), "Missing motor housings"
    assert len(window.motor_housings) == 4, "Should have 4 motors"
    print("✓ Arms and motors created")
    
    # Check propellers
    assert hasattr(window, 'propellers'), "Missing propellers"
    assert len(window.propellers) == 4, "Should have 4 propellers"
    for prop in window.propellers:
        assert 'blade1' in prop, "Missing blade1"
        assert 'blade2' in prop, "Missing blade2"
        assert 'blade3' in prop, "Missing blade3"
        assert 'hub' in prop, "Missing propeller hub"
    print("✓ Propellers created (3 blades each)")
    
    # Check LED components
    assert hasattr(window, 'battery_leds'), "Missing battery LEDs"
    assert len(window.battery_leds) == 4, "Should have 4 battery LEDs"
    assert hasattr(window, 'arm_leds'), "Missing arm LEDs"
    assert len(window.arm_leds) == 4, "Should have 4 arm LEDs"
    print("✓ LED lighting created")
    
    # Check camera gimbal
    assert hasattr(window, 'gimbal'), "Missing camera gimbal"
    assert hasattr(window, 'camera_lens'), "Missing camera lens"
    print("✓ Camera gimbal created")
    
    # Check landing gear
    assert hasattr(window, 'landing_gear'), "Missing landing gear"
    assert len(window.landing_gear) == 4, "Should have 4 landing legs"
    print("✓ Landing gear created")
    
    # Check antenna
    assert hasattr(window, 'antenna'), "Missing antenna"
    print("✓ Antenna created")
    
    # Test that update function works
    test_position = np.array([0.0, 0.0, 5.0])
    test_velocity = np.array([1.0, 0.0, 0.0])
    try:
        window.update_drone_model_position(test_position, test_velocity)
        print("✓ Drone model position update works")
    except Exception as e:
        print(f"✗ Error updating drone position: {e}")
        return False
    
    print("\n✅ All aesthetic improvements verified successfully!")
    print("\nNew features:")
    print("  • Octagonal body plates (top and bottom)")
    print("  • Central hub with blue accent")
    print("  • 4 battery indicator LEDs")
    print("  • Tapered modern arms")
    print("  • Motor housings at arm ends")
    print("  • RGB LED strips on arms (Red/Green/Blue/Yellow)")
    print("  • Camera gimbal underneath")
    print("  • Camera lens")
    print("  • 4 curved landing legs")
    print("  • Antenna on top")
    print("  • 3-blade propellers with realistic airfoil shape")
    
    return True

if __name__ == "__main__":
    try:
        result = test_drone_model_components()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
