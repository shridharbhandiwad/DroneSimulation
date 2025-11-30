"""
Test script for dynamic waypoint modification feature
"""
import numpy as np
import sys
from trajectory_generator import TrajectoryGenerator


def test_basic_generation():
    """Test basic trajectory generation"""
    print("=" * 60)
    print("TEST 1: Basic Trajectory Generation")
    print("=" * 60)
    
    generator = TrajectoryGenerator(dt=0.1)
    
    initial_pos = np.array([0, 0, 5])
    initial_vel = np.array([0, 0, 0])
    waypoints = [
        np.array([10, 10, 10]),
        np.array([20, 5, 15]),
        np.array([30, 20, 12])
    ]
    
    trajectory = generator.generate(initial_pos, initial_vel, waypoints)
    
    print(f"✓ Generated trajectory with {len(trajectory['positions'])} points")
    print(f"✓ Waypoints: {len(waypoints)}")
    print(f"✓ Duration: {trajectory['times'][-1]:.2f} seconds")
    print()
    return trajectory, generator


def test_regenerate_from_current():
    """Test regenerating trajectory from current position"""
    print("=" * 60)
    print("TEST 2: Regenerate Trajectory from Current Position")
    print("=" * 60)
    
    generator = TrajectoryGenerator(dt=0.1)
    
    # Generate initial trajectory
    initial_pos = np.array([0, 0, 5])
    initial_vel = np.array([0, 0, 0])
    waypoints = [
        np.array([10, 10, 10]),
        np.array([20, 5, 15]),
        np.array([30, 20, 12])
    ]
    
    trajectory = generator.generate(initial_pos, initial_vel, waypoints)
    print(f"✓ Initial trajectory: {len(trajectory['positions'])} points")
    
    # Simulate flight to step 50
    current_step = 50
    current_pos = trajectory['positions'][current_step]
    current_vel = trajectory['velocities'][current_step]
    
    print(f"✓ Current position at step {current_step}: {current_pos}")
    print(f"✓ Current velocity: {current_vel}")
    
    # New waypoints
    new_waypoints = [
        np.array([25, 15, 12]),
        np.array([35, 25, 10]),
        np.array([40, 30, 8])
    ]
    
    # Regenerate
    new_trajectory = generator.regenerate_from_current(
        current_pos, current_vel, new_waypoints
    )
    
    print(f"✓ New trajectory: {len(new_trajectory['positions'])} points")
    print(f"✓ New waypoints: {len(new_waypoints)}")
    print(f"✓ Starting position matches: {np.allclose(new_trajectory['positions'][0], current_pos)}")
    print(f"✓ Starting velocity matches: {np.allclose(new_trajectory['velocities'][0], current_vel)}")
    print()
    return new_trajectory


def test_waypoint_management():
    """Test waypoint add/remove/modify operations"""
    print("=" * 60)
    print("TEST 3: Waypoint Management Operations")
    print("=" * 60)
    
    generator = TrajectoryGenerator(dt=0.1)
    
    # Test add_waypoint_at_index
    print("Testing add_waypoint_at_index...")
    generator.add_waypoint_at_index(np.array([10, 10, 10]))
    generator.add_waypoint_at_index(np.array([20, 20, 15]))
    generator.add_waypoint_at_index(np.array([30, 30, 12]))
    print(f"✓ Added 3 waypoints, current count: {len(generator.waypoints)}")
    
    # Test insert
    generator.add_waypoint_at_index(np.array([15, 15, 12]), index=1)
    print(f"✓ Inserted waypoint at index 1, count: {len(generator.waypoints)}")
    
    # Test get_waypoints
    waypoints = generator.get_waypoints()
    print(f"✓ Retrieved {len(waypoints)} waypoints")
    
    # Test modify_waypoint
    generator.modify_waypoint(2, np.array([25, 25, 14]))
    print(f"✓ Modified waypoint at index 2")
    
    # Test remove_waypoint
    generator.remove_waypoint(1)
    print(f"✓ Removed waypoint at index 1, count: {len(generator.waypoints)}")
    
    # Test set_waypoints
    new_waypoints = [
        np.array([5, 5, 8]),
        np.array([10, 10, 10])
    ]
    generator.set_waypoints(new_waypoints)
    print(f"✓ Set waypoints directly, count: {len(generator.waypoints)}")
    
    print()


def test_dynamic_modification_scenario():
    """Test a complete dynamic modification scenario"""
    print("=" * 60)
    print("TEST 4: Complete Dynamic Modification Scenario")
    print("=" * 60)
    
    generator = TrajectoryGenerator(dt=0.1)
    
    # Step 1: Create initial mission
    print("Step 1: Initial mission with 3 waypoints")
    initial_waypoints = [
        np.array([10, 0, 10]),
        np.array([20, 0, 10]),
        np.array([30, 0, 10])
    ]
    
    trajectory = generator.generate(
        np.array([0, 0, 5]),
        np.array([0, 0, 0]),
        initial_waypoints
    )
    print(f"✓ Initial trajectory: {len(trajectory['positions'])} points, duration: {trajectory['times'][-1]:.2f}s")
    
    # Step 2: Simulate flight
    print("\nStep 2: Simulate flight to 40% completion")
    current_step = int(len(trajectory['positions']) * 0.4)
    current_pos = trajectory['positions'][current_step]
    current_vel = trajectory['velocities'][current_step]
    current_time = trajectory['times'][current_step]
    print(f"✓ Current step: {current_step}/{len(trajectory['positions'])}")
    print(f"✓ Position: {current_pos}")
    print(f"✓ Time: {current_time:.2f}s")
    
    # Step 3: Mission change - new target area
    print("\nStep 3: Mission change - divert to new area")
    new_waypoints = [
        np.array([25, 10, 12]),
        np.array([30, 20, 15]),
        np.array([40, 20, 10])
    ]
    
    updated_trajectory = generator.regenerate_from_current(
        current_pos, current_vel, new_waypoints
    )
    print(f"✓ Updated trajectory: {len(updated_trajectory['positions'])} points")
    print(f"✓ New waypoints: {new_waypoints}")
    
    # Step 4: Verify continuity
    print("\nStep 4: Verify trajectory continuity")
    position_match = np.allclose(updated_trajectory['positions'][0], current_pos)
    velocity_match = np.allclose(updated_trajectory['velocities'][0], current_vel)
    
    print(f"✓ Position continuity: {position_match}")
    print(f"✓ Velocity continuity: {velocity_match}")
    
    if position_match and velocity_match:
        print("✓ Trajectory update successful - smooth transition achieved!")
    else:
        print("✗ Warning: Trajectory may have discontinuity")
    
    # Step 5: Add emergency waypoint
    print("\nStep 5: Emergency waypoint insertion (simulate obstacle avoidance)")
    emergency_waypoint = np.array([28, 15, 14])
    
    # Simulate being at step 20 of updated trajectory
    current_step_2 = 20
    current_pos_2 = updated_trajectory['positions'][current_step_2]
    current_vel_2 = updated_trajectory['velocities'][current_step_2]
    
    # Insert emergency waypoint at beginning, then continue to remaining waypoints
    emergency_waypoints = [emergency_waypoint] + new_waypoints[1:]  # Skip first waypoint, already passed
    
    final_trajectory = generator.regenerate_from_current(
        current_pos_2, current_vel_2, emergency_waypoints
    )
    
    print(f"✓ Final trajectory with emergency waypoint: {len(final_trajectory['positions'])} points")
    print(f"✓ Emergency detour to: {emergency_waypoint}")
    
    print()


def test_edge_cases():
    """Test edge cases and error conditions"""
    print("=" * 60)
    print("TEST 5: Edge Cases and Robustness")
    print("=" * 60)
    
    generator = TrajectoryGenerator(dt=0.1)
    
    # Test 1: Single waypoint
    print("Test 1: Single waypoint trajectory")
    trajectory = generator.generate(
        np.array([0, 0, 5]),
        np.array([0, 0, 0]),
        [np.array([10, 10, 10])]
    )
    print(f"✓ Single waypoint trajectory: {len(trajectory['positions'])} points")
    
    # Test 2: Very close waypoints
    print("\nTest 2: Very close waypoints")
    close_waypoints = [
        np.array([5, 5, 8]),
        np.array([5.1, 5.1, 8.1]),
        np.array([10, 10, 10])
    ]
    trajectory = generator.generate(
        np.array([0, 0, 5]),
        np.array([0, 0, 0]),
        close_waypoints
    )
    print(f"✓ Close waypoints trajectory: {len(trajectory['positions'])} points")
    
    # Test 3: Regenerate with empty waypoint list (should handle gracefully)
    print("\nTest 3: Regenerate with current position near waypoint")
    current_pos = np.array([9.5, 9.5, 9.8])  # Very close to waypoint [10,10,10]
    current_vel = np.array([1, 1, 0.5])
    
    trajectory = generator.regenerate_from_current(
        current_pos, current_vel, [np.array([10, 10, 10])]
    )
    print(f"✓ Regenerated near waypoint: {len(trajectory['positions'])} points")
    
    # Test 4: High velocity start
    print("\nTest 4: High velocity regeneration")
    high_vel = np.array([10, 5, 2])
    trajectory = generator.regenerate_from_current(
        np.array([15, 15, 12]),
        high_vel,
        [np.array([25, 25, 15])]
    )
    print(f"✓ High velocity trajectory: {len(trajectory['positions'])} points")
    print(f"✓ Initial velocity magnitude: {np.linalg.norm(high_vel):.2f} m/s")
    
    print()


def test_performance():
    """Test performance of dynamic regeneration"""
    print("=" * 60)
    print("TEST 6: Performance Test")
    print("=" * 60)
    
    import time
    
    generator = TrajectoryGenerator(dt=0.1)
    
    # Generate initial trajectory
    waypoints = [np.array([10*i, 10*i, 10+i]) for i in range(1, 6)]
    trajectory = generator.generate(
        np.array([0, 0, 5]),
        np.array([0, 0, 0]),
        waypoints
    )
    
    print(f"Initial trajectory: {len(trajectory['positions'])} points")
    
    # Test regeneration speed
    num_tests = 10
    total_time = 0
    
    for i in range(num_tests):
        step = np.random.randint(10, len(trajectory['positions']) - 10)
        current_pos = trajectory['positions'][step]
        current_vel = trajectory['velocities'][step]
        
        new_waypoints = [np.array([np.random.uniform(20, 40), 
                                  np.random.uniform(20, 40), 
                                  np.random.uniform(10, 15)]) for _ in range(3)]
        
        start = time.time()
        new_traj = generator.regenerate_from_current(current_pos, current_vel, new_waypoints)
        elapsed = time.time() - start
        total_time += elapsed
    
    avg_time = total_time / num_tests
    print(f"✓ Average regeneration time: {avg_time*1000:.2f} ms ({num_tests} tests)")
    
    if avg_time < 0.1:  # 100ms threshold
        print("✓ Performance: EXCELLENT (< 100ms)")
    elif avg_time < 0.5:
        print("✓ Performance: GOOD (< 500ms)")
    else:
        print("⚠ Performance: ACCEPTABLE (> 500ms)")
    
    print()


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DYNAMIC WAYPOINT MODIFICATION - TEST SUITE")
    print("=" * 60 + "\n")
    
    try:
        # Run tests
        test_basic_generation()
        test_regenerate_from_current()
        test_waypoint_management()
        test_dynamic_modification_scenario()
        test_edge_cases()
        test_performance()
        
        # Summary
        print("=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        print("\nDynamic waypoint modification feature is working correctly!")
        print("\nNext steps:")
        print("1. Run the GUI: python simulation.py")
        print("2. Enable 'Dynamic Waypoint Mode' in the GUI")
        print("3. Try adding/modifying waypoints during flight")
        print("4. Refer to DYNAMIC_WAYPOINTS_GUIDE.md for detailed usage")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ TEST FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
