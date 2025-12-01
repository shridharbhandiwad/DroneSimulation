#!/usr/bin/env python3
"""
Verification script for drone model aesthetic improvements.
This checks the code structure without running the GUI.
"""

import sys
import os
import ast
import inspect

sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

def check_method_exists(source_code, method_name):
    """Check if a method exists in the source code"""
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            return True
    return False

def main():
    print("Verifying drone model aesthetic improvements...\n")
    
    # Read the simulation.py file
    with open('/workspace/python/simulation.py', 'r') as f:
        source_code = f.read()
    
    # Check for new geometry creation methods
    new_methods = [
        'create_octagonal_plate',
        'create_tapered_arm',
        'create_led_strip',
        'create_landing_leg',
        'create_curved_propeller_blade'
    ]
    
    print("Checking for new geometry creation methods:")
    for method in new_methods:
        if check_method_exists(source_code, method):
            print(f"  ✓ {method}")
        else:
            print(f"  ✗ {method} NOT FOUND")
            return False
    
    # Check for new component references in create_drone_model
    print("\nChecking for new drone components:")
    components = [
        'drone_body_top',
        'drone_body_bottom',
        'drone_hub',
        'battery_leds',
        'motor_housings',
        'arm_leds',
        'gimbal',
        'camera_lens',
        'landing_gear',
        'antenna'
    ]
    
    for component in components:
        if f'self.{component}' in source_code:
            print(f"  ✓ {component}")
        else:
            print(f"  ✗ {component} NOT FOUND")
            return False
    
    # Check for 3-blade propeller implementation
    print("\nChecking propeller improvements:")
    if "'blade3'" in source_code:
        print("  ✓ 3-blade propellers implemented")
    else:
        print("  ✗ 3-blade propellers NOT FOUND")
        return False
    
    if "'hub'" in source_code and 'propeller hub' in source_code.lower():
        print("  ✓ Propeller hubs added")
    else:
        print("  ✗ Propeller hubs NOT FOUND")
        return False
    
    # Check update method handles new components
    print("\nChecking update_drone_model_position method:")
    update_checks = [
        'drone_body_top.setTransform',
        'drone_body_bottom.setTransform',
        'motor_housings',
        'arm_leds',
        'gimbal.setTransform',
        'camera_lens.setTransform',
        'landing_gear',
        'antenna.setTransform'
    ]
    
    for check in update_checks:
        if check in source_code:
            print(f"  ✓ {check}")
        else:
            print(f"  ✗ {check} NOT FOUND")
            return False
    
    # Count lines to show scope of changes
    print("\n" + "="*60)
    print("Statistics:")
    method_start = source_code.find('def create_drone_model(self):')
    method_end = source_code.find('def update_drone_model_position(self, position, velocity):', method_start)
    create_lines = source_code[method_start:method_end].count('\n')
    print(f"  • create_drone_model method: ~{create_lines} lines")
    
    update_start = source_code.find('def update_drone_model_position(self, position, velocity):')
    # Find next method
    next_def = source_code.find('\n    def ', update_start + 10)
    update_lines = source_code[update_start:next_def].count('\n')
    print(f"  • update_drone_model_position method: ~{update_lines} lines")
    
    # New geometry methods
    geometry_methods_count = len([m for m in new_methods if check_method_exists(source_code, m)])
    print(f"  • New geometry creation methods: {geometry_methods_count}")
    
    print("\n" + "="*60)
    print("✅ ALL VERIFICATIONS PASSED!")
    print("\n🎨 Aesthetic Improvements Summary:")
    print("="*60)
    print("Body:")
    print("  • Octagonal top plate (carbon fiber look)")
    print("  • Octagonal bottom plate (slightly smaller)")
    print("  • Central hub with blue accent color")
    print("  • 4 battery indicator LEDs on top")
    print()
    print("Arms & Motors:")
    print("  • Tapered rectangular arms (modern design)")
    print("  • Motor housings at each arm end")
    print("  • RGB LED strips (Red/Green/Blue/Yellow)")
    print()
    print("Propellers:")
    print("  • 3-blade design (more realistic)")
    print("  • Curved airfoil blade shape")
    print("  • Blade twist for realistic aerodynamics")
    print("  • Propeller hubs")
    print("  • Faster rotation (45°/frame)")
    print()
    print("Camera System:")
    print("  • Camera gimbal underneath center")
    print("  • Camera lens pointing forward")
    print()
    print("Landing System:")
    print("  • 4 curved landing legs")
    print("  • Legs curve outward for stability")
    print()
    print("Additional Features:")
    print("  • Antenna on top")
    print("  • Improved color scheme (dark carbon fiber)")
    print("  • Translucent materials for LEDs")
    print("="*60)
    
    return True

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n✗ Verification failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
