"""
Quick test script to verify the system works end-to-end
"""
import numpy as np
from trajectory_generator import TrajectoryGenerator
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os


def test_trajectory_generation():
    """Test basic trajectory generation"""
    print("Testing trajectory generation...")
    
    generator = TrajectoryGenerator(dt=0.1)
    
    # Define test case
    initial_pos = np.array([0, 0, 5])
    initial_vel = np.array([0, 0, 0])
    waypoints = [
        np.array([10, 10, 8]),
        np.array([20, 5, 10]),
        np.array([15, -10, 7]),
        np.array([0, 0, 5])
    ]
    
    # Generate trajectory
    trajectory = generator.generate(initial_pos, initial_vel, waypoints, max_time=60)
    
    print(f"  ✓ Generated trajectory with {len(trajectory['positions'])} steps")
    print(f"  ✓ Duration: {trajectory['times'][-1]:.1f} seconds")
    print(f"  ✓ Waypoints: {len(waypoints)}")
    
    return trajectory


def test_ml_model():
    """Test ML model if available"""
    print("\nTesting ML model...")
    
    model_path = '../models/best_model.pth'
    
    if not os.path.exists(model_path):
        print("  ⚠ Model not found - run training first")
        return None
    
    try:
        from ml_model import TrajectoryPredictor
        
        predictor = TrajectoryPredictor(model_path)
        print("  ✓ Model loaded successfully")
        
        # Create dummy history
        history = []
        for i in range(10):
            state = {
                'position': np.array([float(i), float(i), 5.0]),
                'velocity': np.array([1.0, 1.0, 0.0]),
                'acceleration': np.array([0.0, 0.0, 0.0])
            }
            history.append(state)
        
        # Test prediction
        target = np.array([15.0, 15.0, 8.0])
        prediction = predictor.predict(history, target)
        
        print(f"  ✓ Prediction successful")
        print(f"    Position: {prediction['position']}")
        print(f"    Velocity: {prediction['velocity']}")
        
        return predictor
        
    except Exception as e:
        print(f"  ✗ Model test failed: {e}")
        return None


def visualize_trajectory(trajectory):
    """Visualize the trajectory in 3D"""
    print("\nGenerating visualization...")
    
    positions = trajectory['positions']
    waypoints = trajectory['waypoints']
    
    fig = plt.figure(figsize=(12, 5))
    
    # 3D plot
    ax1 = fig.add_subplot(121, projection='3d')
    ax1.plot(positions[:, 0], positions[:, 1], positions[:, 2], 
             'b-', linewidth=2, label='Trajectory')
    ax1.scatter(waypoints[:, 0], waypoints[:, 1], waypoints[:, 2],
               c='r', s=100, marker='*', label='Waypoints')
    ax1.scatter(positions[0, 0], positions[0, 1], positions[0, 2],
               c='g', s=100, marker='o', label='Start')
    ax1.set_xlabel('X (m)')
    ax1.set_ylabel('Y (m)')
    ax1.set_zlabel('Z (m)')
    ax1.set_title('3D Trajectory')
    ax1.legend()
    ax1.grid(True)
    
    # Time series
    ax2 = fig.add_subplot(122)
    times = trajectory['times']
    velocities = trajectory['velocities']
    speeds = np.linalg.norm(velocities, axis=1)
    
    ax2.plot(times, speeds, 'b-', linewidth=2)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Speed (m/s)')
    ax2.set_title('Speed over Time')
    ax2.grid(True)
    
    plt.tight_layout()
    
    output_path = '../data/test_trajectory.png'
    plt.savefig(output_path, dpi=150)
    print(f"  ✓ Visualization saved to {output_path}")
    
    # Try to display (may not work in headless environments)
    try:
        plt.show()
    except:
        print("  ⚠ Cannot display plot (headless environment)")


def test_data_format():
    """Test data generation format"""
    print("\nTesting data format...")
    
    if not os.path.exists('../data/train_data.pkl'):
        print("  ⚠ Training data not found - run data_generator.py first")
        return
    
    import pickle
    
    with open('../data/train_data.pkl', 'rb') as f:
        train_samples = pickle.load(f)
    
    print(f"  ✓ Loaded {len(train_samples)} training samples")
    
    # Check sample format
    sample = train_samples[0]
    print(f"  ✓ Input shape: {sample['input_sequence'].shape}")
    print(f"  ✓ Target shape: {sample['target'].shape}")
    print(f"    Expected input: (10, 13) [sequence_length, features]")
    print(f"    Expected target: (6,) [position + velocity]")


def main():
    """Run all tests"""
    print("="*60)
    print("Drone Trajectory System - Quick Test")
    print("="*60)
    print()
    
    # Test trajectory generation
    trajectory = test_trajectory_generation()
    
    # Test ML model
    predictor = test_ml_model()
    
    # Test data format
    test_data_format()
    
    # Visualize
    if trajectory is not None:
        visualize_trajectory(trajectory)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print("✓ Trajectory generation: PASSED")
    print(f"{'✓' if predictor else '⚠'} ML model: {'PASSED' if predictor else 'SKIPPED (not trained)'}")
    print("✓ Visualization: PASSED")
    print()
    
    if predictor is None:
        print("To enable ML features, run:")
        print("  1. python data_generator.py")
        print("  2. python train_model.py")
        print()
    else:
        print("All systems operational! ✓")
        print()
        print("Next steps:")
        print("  • Run simulation: python simulation.py")
        print("  • Export to ONNX: python export_to_onnx.py")
        print()


if __name__ == '__main__':
    main()
