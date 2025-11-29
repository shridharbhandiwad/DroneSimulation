"""
Generate training data for trajectory prediction model
"""
import numpy as np
import pickle
import os
from typing import List, Dict
from trajectory_generator import TrajectoryGenerator
from tqdm import tqdm


def generate_random_waypoints(num_waypoints: int = 5, 
                              area_size: float = 50.0,
                              min_height: float = 2.0,
                              max_height: float = 20.0) -> List[np.ndarray]:
    """Generate random waypoints in 3D space"""
    waypoints = []
    for _ in range(num_waypoints):
        x = np.random.uniform(-area_size, area_size)
        y = np.random.uniform(-area_size, area_size)
        z = np.random.uniform(min_height, max_height)
        waypoints.append(np.array([x, y, z]))
    return waypoints


def create_training_sequences(trajectory: Dict, sequence_length: int = 10) -> List[Dict]:
    """
    Create training sequences from trajectory data
    
    Args:
        trajectory: Trajectory dict from TrajectoryGenerator
        sequence_length: Length of input sequence
        
    Returns:
        List of training samples, each with 'input_sequence' and 'target'
    """
    samples = []
    
    positions = trajectory['positions']
    velocities = trajectory['velocities']
    accelerations = trajectory['accelerations']
    waypoint_indices = trajectory['waypoint_indices']
    waypoints = trajectory['waypoints']
    
    for i in range(sequence_length, len(positions)):
        # Input sequence
        input_seq = []
        for j in range(i - sequence_length, i):
            wp_idx = min(waypoint_indices[j], len(waypoints) - 1)
            target_wp = waypoints[wp_idx]
            dist_to_wp = np.linalg.norm(positions[j] - target_wp)
            
            features = np.concatenate([
                positions[j],
                velocities[j],
                accelerations[j],
                target_wp,
                [dist_to_wp]
            ])
            input_seq.append(features)
        
        # Target (next position and velocity)
        target = np.concatenate([
            positions[i],
            velocities[i]
        ])
        
        samples.append({
            'input_sequence': np.array(input_seq, dtype=np.float32),
            'target': np.array(target, dtype=np.float32)
        })
    
    return samples


def generate_dataset(num_trajectories: int = 1000, 
                     output_dir: str = '../data',
                     sequence_length: int = 10) -> Dict:
    """
    Generate complete training dataset
    
    Args:
        num_trajectories: Number of trajectories to generate
        output_dir: Directory to save data
        sequence_length: Length of input sequences
        
    Returns:
        Dataset statistics
    """
    os.makedirs(output_dir, exist_ok=True)
    
    generator = TrajectoryGenerator(dt=0.1)
    all_samples = []
    
    print(f"Generating {num_trajectories} trajectories...")
    
    for i in tqdm(range(num_trajectories)):
        # Random initial conditions
        initial_pos = np.array([
            np.random.uniform(-5, 5),
            np.random.uniform(-5, 5),
            np.random.uniform(2, 5)
        ])
        initial_vel = np.random.uniform(-2, 2, 3)
        
        # Random waypoints
        num_waypoints = np.random.randint(3, 8)
        waypoints = generate_random_waypoints(num_waypoints)
        
        # Generate trajectory
        trajectory = generator.generate(initial_pos, initial_vel, waypoints)
        
        # Add noise for data augmentation
        if np.random.random() < 0.3:  # 30% with noise
            trajectory = generator.add_noise(trajectory, 0.1, 0.05)
        
        # Create training sequences
        samples = create_training_sequences(trajectory, sequence_length)
        all_samples.extend(samples)
    
    # Shuffle samples
    np.random.shuffle(all_samples)
    
    # Split into train/val/test
    n_total = len(all_samples)
    n_train = int(0.7 * n_total)
    n_val = int(0.15 * n_total)
    
    train_samples = all_samples[:n_train]
    val_samples = all_samples[n_train:n_train+n_val]
    test_samples = all_samples[n_train+n_val:]
    
    # Calculate normalization statistics from training data
    all_positions = np.array([s['target'][:3] for s in train_samples])
    all_velocities = np.array([s['target'][3:6] for s in train_samples])
    
    pos_mean = np.mean(all_positions, axis=0)
    pos_std = np.std(all_positions, axis=0)
    vel_mean = np.mean(all_velocities, axis=0)
    vel_std = np.std(all_velocities, axis=0)
    
    normalization = {
        'pos_mean': pos_mean,
        'pos_std': pos_std,
        'vel_mean': vel_mean,
        'vel_std': vel_std
    }
    
    # Save datasets
    print(f"\nSaving datasets...")
    print(f"  Training samples: {len(train_samples)}")
    print(f"  Validation samples: {len(val_samples)}")
    print(f"  Test samples: {len(test_samples)}")
    
    with open(os.path.join(output_dir, 'train_data.pkl'), 'wb') as f:
        pickle.dump(train_samples, f)
    
    with open(os.path.join(output_dir, 'val_data.pkl'), 'wb') as f:
        pickle.dump(val_samples, f)
    
    with open(os.path.join(output_dir, 'test_data.pkl'), 'wb') as f:
        pickle.dump(test_samples, f)
    
    with open(os.path.join(output_dir, 'normalization.pkl'), 'wb') as f:
        pickle.dump(normalization, f)
    
    stats = {
        'num_trajectories': num_trajectories,
        'total_samples': n_total,
        'train_samples': len(train_samples),
        'val_samples': len(val_samples),
        'test_samples': len(test_samples),
        'sequence_length': sequence_length
    }
    
    print(f"\nDataset generation complete!")
    print(f"Data saved to: {output_dir}")
    
    return stats


if __name__ == '__main__':
    # Generate dataset
    stats = generate_dataset(num_trajectories=1000, output_dir='../data')
    print(f"\nDataset statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
