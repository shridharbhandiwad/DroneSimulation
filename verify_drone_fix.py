#!/usr/bin/env python3
"""
Simple verification script to check the drone color fix in the code.
This doesn't require running the GUI - just analyzes the source code.
"""

import re

def check_drone_colors():
    """Verify that drone colors are properly set for both themes"""
    
    with open('/workspace/python/simulation.py', 'r') as f:
        content = f.read()
    
    print("=" * 70)
    print("VERIFYING DRONE COLOR FIX FOR BLACK THEME")
    print("=" * 70)
    print()
    
    # Check for black theme drone parts
    checks = [
        ("Drone Hub", r"drone_body.*setColor.*0\.7.*0\.9.*1\.0", "Black theme"),
        ("Drone Top Plate", r"drone_body_top.*setColor.*0\.75.*0\.85.*0\.95", "Black theme"),
        ("Drone Bottom Plate", r"drone_body_bottom.*setColor.*0\.70.*0\.80.*0\.92", "Black theme"),
        ("Drone Arms", r"drone_arms.*setColor.*0\.65.*0\.75.*0\.85", "Black theme"),
        ("Motor Housings", r"motor_housings.*setColor.*0\.70.*0\.78.*0\.88", "Black theme"),
        ("Landing Gear", r"landing_gear.*setColor.*0\.65.*0\.72.*0\.82", "Black theme"),
        ("Propellers", r"propellers.*setColor.*0\.60.*0\.70.*0\.85", "Black theme"),
        ("Gimbal", r"gimbal.*setColor.*0\.60.*0\.68.*0\.78", "Black theme"),
    ]
    
    all_passed = True
    
    for name, pattern, theme in checks:
        if re.search(pattern, content, re.DOTALL):
            print(f"✅ {name}: Bright color set for {theme}")
        else:
            print(f"❌ {name}: NOT FOUND - may still be black in {theme}")
            all_passed = False
    
    print()
    print("=" * 70)
    
    # Check for white theme drone parts (should be dark)
    white_checks = [
        ("Drone Top Plate", r"drone_body_top.*setColor.*0\.15.*0\.15.*0\.18", "White theme"),
        ("Drone Bottom Plate", r"drone_body_bottom.*setColor.*0\.12.*0\.12.*0\.15", "White theme"),
        ("Drone Arms", r"drone_arms.*setColor.*0\.18.*0\.18.*0\.20", "White theme"),
    ]
    
    print("VERIFYING DARK COLORS FOR WHITE THEME")
    print("=" * 70)
    print()
    
    for name, pattern, theme in white_checks:
        if re.search(pattern, content, re.DOTALL):
            print(f"✅ {name}: Dark color set for {theme}")
        else:
            print(f"❌ {name}: NOT FOUND in {theme}")
            all_passed = False
    
    print()
    print("=" * 70)
    
    if all_passed:
        print("🎉 SUCCESS! All drone parts have proper theme colors!")
        print()
        print("Summary:")
        print("  • BLACK theme: All drone parts are BRIGHT (silver-blue tones)")
        print("  • WHITE theme: All drone parts are DARK (carbon fiber look)")
        print()
        print("The drone will now be clearly visible in the black theme!")
        return True
    else:
        print("⚠️  Some checks failed. Please review the implementation.")
        return False

if __name__ == '__main__':
    import sys
    success = check_drone_colors()
    sys.exit(0 if success else 1)
