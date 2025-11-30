"""
Export trajectory dataset from pickle format to CSV
"""
import numpy as np
import pandas as pd
import pickle
import os
from typing import Dict, List
import argparse


def flatten_sample(sample: Dict, sequence_length: int = 10) -> Dict:
    """
    Flatten a single sample into a dictionary suitable for DataFrame
    
    Args:
        sample: Sample dict with 'input_sequence' and 'target'
        sequence_length: Length of input sequence
        
    Returns:
        Flattened dict with all features
    """
    flattened = {}
    
    # Flatten input sequence
    # Each timestep has 13 features: pos(3), vel(3), acc(3), target_wp(3), dist(1)
    feature_names = ['pos_x', 'pos_y', 'pos_z', 
                     'vel_x', 'vel_y', 'vel_z',
                     'acc_x', 'acc_y', 'acc_z',
                     'target_wp_x', 'target_wp_y', 'target_wp_z',
                     'dist_to_wp']
    
    input_seq = sample['input_sequence']
    for t in range(sequence_length):
        for i, feature_name in enumerate(feature_names):
            flattened[f't{t}_{feature_name}'] = input_seq[t, i]
    
    # Target features: next position(3) and velocity(3)
    target = sample['target']
    flattened['target_pos_x'] = target[0]
    flattened['target_pos_y'] = target[1]
    flattened['target_pos_z'] = target[2]
    flattened['target_vel_x'] = target[3]
    flattened['target_vel_y'] = target[4]
    flattened['target_vel_z'] = target[5]
    
    return flattened


def export_dataset_to_csv(data_dir: str = '../data', 
                          output_dir: str = '../data/csv',
                          sequence_length: int = 10):
    """
    Export dataset from pickle to CSV format
    
    Args:
        data_dir: Directory containing pickle files
        output_dir: Directory to save CSV files
        sequence_length: Length of input sequences
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load and export train data
    print("Exporting training data...")
    with open(os.path.join(data_dir, 'train_data.pkl'), 'rb') as f:
        train_samples = pickle.load(f)
    
    train_flattened = [flatten_sample(s, sequence_length) for s in train_samples]
    train_df = pd.DataFrame(train_flattened)
    train_csv_path = os.path.join(output_dir, 'train_data.csv')
    train_df.to_csv(train_csv_path, index=False)
    print(f"  Saved {len(train_df)} samples to {train_csv_path}")
    
    # Load and export validation data
    print("Exporting validation data...")
    with open(os.path.join(data_dir, 'val_data.pkl'), 'rb') as f:
        val_samples = pickle.load(f)
    
    val_flattened = [flatten_sample(s, sequence_length) for s in val_samples]
    val_df = pd.DataFrame(val_flattened)
    val_csv_path = os.path.join(output_dir, 'val_data.csv')
    val_df.to_csv(val_csv_path, index=False)
    print(f"  Saved {len(val_df)} samples to {val_csv_path}")
    
    # Load and export test data
    print("Exporting test data...")
    with open(os.path.join(data_dir, 'test_data.pkl'), 'rb') as f:
        test_samples = pickle.load(f)
    
    test_flattened = [flatten_sample(s, sequence_length) for s in test_samples]
    test_df = pd.DataFrame(test_flattened)
    test_csv_path = os.path.join(output_dir, 'test_data.csv')
    test_df.to_csv(test_csv_path, index=False)
    print(f"  Saved {len(test_df)} samples to {test_csv_path}")
    
    # Export normalization statistics
    print("Exporting normalization statistics...")
    with open(os.path.join(data_dir, 'normalization.pkl'), 'rb') as f:
        normalization = pickle.load(f)
    
    norm_data = {
        'statistic': ['pos_mean_x', 'pos_mean_y', 'pos_mean_z',
                     'pos_std_x', 'pos_std_y', 'pos_std_z',
                     'vel_mean_x', 'vel_mean_y', 'vel_mean_z',
                     'vel_std_x', 'vel_std_y', 'vel_std_z'],
        'value': list(normalization['pos_mean']) + 
                list(normalization['pos_std']) +
                list(normalization['vel_mean']) + 
                list(normalization['vel_std'])
    }
    norm_df = pd.DataFrame(norm_data)
    norm_csv_path = os.path.join(output_dir, 'normalization.csv')
    norm_df.to_csv(norm_csv_path, index=False)
    print(f"  Saved normalization statistics to {norm_csv_path}")
    
    # Create a metadata file
    metadata = {
        'parameter': ['sequence_length', 'input_features_per_timestep', 
                     'output_features', 'train_samples', 'val_samples', 'test_samples',
                     'total_input_features', 'total_columns'],
        'value': [sequence_length, 13, 6, len(train_df), len(val_df), len(test_df),
                 sequence_length * 13, sequence_length * 13 + 6]
    }
    metadata_df = pd.DataFrame(metadata)
    metadata_csv_path = os.path.join(output_dir, 'dataset_metadata.csv')
    metadata_df.to_csv(metadata_csv_path, index=False)
    print(f"  Saved metadata to {metadata_csv_path}")
    
    print(f"\nExport complete!")
    print(f"CSV files saved to: {output_dir}")
    print(f"\nDataset structure:")
    print(f"  - Each row represents one training sample")
    print(f"  - Input sequence: {sequence_length} timesteps x 13 features = {sequence_length * 13} columns")
    print(f"  - Target: 6 features (next position + velocity)")
    print(f"  - Total columns: {sequence_length * 13 + 6}")
    print(f"\nFeatures per timestep:")
    print(f"  - Position (x, y, z)")
    print(f"  - Velocity (x, y, z)")
    print(f"  - Acceleration (x, y, z)")
    print(f"  - Target waypoint (x, y, z)")
    print(f"  - Distance to waypoint")


def export_trajectories_to_csv(data_dir: str = '../data',
                               output_dir: str = '../data/csv'):
    """
    Export raw trajectory data if available
    
    Args:
        data_dir: Directory containing trajectory files
        output_dir: Directory to save CSV files
    """
    trajectory_file = os.path.join(data_dir, 'trajectories.pkl')
    
    if not os.path.exists(trajectory_file):
        print(f"\nNo raw trajectory file found at {trajectory_file}")
        print("Skipping trajectory export.")
        return
    
    print("\nExporting raw trajectories...")
    with open(trajectory_file, 'rb') as f:
        trajectories = pickle.load(f)
    
    # Export each trajectory
    for i, traj in enumerate(trajectories):
        traj_data = {
            'time': traj['times'],
            'pos_x': traj['positions'][:, 0],
            'pos_y': traj['positions'][:, 1],
            'pos_z': traj['positions'][:, 2],
            'vel_x': traj['velocities'][:, 0],
            'vel_y': traj['velocities'][:, 1],
            'vel_z': traj['velocities'][:, 2],
            'acc_x': traj['accelerations'][:, 0],
            'acc_y': traj['accelerations'][:, 1],
            'acc_z': traj['accelerations'][:, 2],
            'waypoint_idx': traj['waypoint_indices']
        }
        
        traj_df = pd.DataFrame(traj_data)
        traj_csv_path = os.path.join(output_dir, f'trajectory_{i:04d}.csv')
        traj_df.to_csv(traj_csv_path, index=False)
        
        if i == 0:
            print(f"  Saved trajectory {i} to {traj_csv_path}")
        elif i == len(trajectories) - 1:
            print(f"  Saved trajectory {i} to {traj_csv_path}")
    
    print(f"  Total trajectories exported: {len(trajectories)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export trajectory dataset to CSV')
    parser.add_argument('--data_dir', type=str, default='../data',
                       help='Directory containing pickle files')
    parser.add_argument('--output_dir', type=str, default='../data/csv',
                       help='Directory to save CSV files')
    parser.add_argument('--sequence_length', type=int, default=10,
                       help='Length of input sequences')
    parser.add_argument('--export_trajectories', action='store_true',
                       help='Also export raw trajectory data if available')
    
    args = parser.parse_args()
    
    # Check if data directory exists
    if not os.path.exists(args.data_dir):
        print(f"Error: Data directory not found: {args.data_dir}")
        print("Please generate the dataset first using data_generator.py")
        exit(1)
    
    # Check if required files exist
    required_files = ['train_data.pkl', 'val_data.pkl', 'test_data.pkl', 'normalization.pkl']
    for filename in required_files:
        filepath = os.path.join(args.data_dir, filename)
        if not os.path.exists(filepath):
            print(f"Error: Required file not found: {filepath}")
            print("Please generate the dataset first using data_generator.py")
            exit(1)
    
    # Export dataset
    export_dataset_to_csv(args.data_dir, args.output_dir, args.sequence_length)
    
    # Optionally export raw trajectories
    if args.export_trajectories:
        export_trajectories_to_csv(args.data_dir, args.output_dir)
