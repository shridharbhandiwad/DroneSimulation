"""
Utility functions for drone trajectory system
"""
import numpy as np
from typing import List, Tuple


def normalize_vector(v: np.ndarray) -> np.ndarray:
    """Normalize a vector to unit length"""
    norm = np.linalg.norm(v)
    if norm < 1e-6:
        return v
    return v / norm


def distance_3d(p1: np.ndarray, p2: np.ndarray) -> float:
    """Calculate Euclidean distance between two 3D points"""
    return np.linalg.norm(p2 - p1)


def interpolate_waypoints(waypoints: List[np.ndarray], num_points: int) -> np.ndarray:
    """Interpolate between waypoints to create smooth path"""
    if len(waypoints) < 2:
        return np.array(waypoints)
    
    total_distance = sum(distance_3d(waypoints[i], waypoints[i+1]) 
                         for i in range(len(waypoints)-1))
    
    interpolated = []
    for i in range(len(waypoints) - 1):
        start = waypoints[i]
        end = waypoints[i + 1]
        segment_distance = distance_3d(start, end)
        segment_points = max(2, int(num_points * segment_distance / total_distance))
        
        for j in range(segment_points):
            t = j / segment_points
            point = start + t * (end - start)
            interpolated.append(point)
    
    interpolated.append(waypoints[-1])
    return np.array(interpolated)


def calculate_heading(position: np.ndarray, target: np.ndarray) -> Tuple[float, float]:
    """
    Calculate heading angles (yaw, pitch) from position to target
    Returns: (yaw, pitch) in radians
    """
    direction = target - position
    
    # Yaw (rotation around z-axis)
    yaw = np.arctan2(direction[1], direction[0])
    
    # Pitch (rotation around y-axis)
    horizontal_dist = np.sqrt(direction[0]**2 + direction[1]**2)
    pitch = np.arctan2(direction[2], horizontal_dist)
    
    return yaw, pitch


def limit_acceleration(velocity: np.ndarray, target_velocity: np.ndarray, 
                       max_acceleration: float, dt: float) -> np.ndarray:
    """Limit acceleration to physically realistic values"""
    desired_accel = (target_velocity - velocity) / dt
    accel_magnitude = np.linalg.norm(desired_accel)
    
    if accel_magnitude > max_acceleration:
        desired_accel = desired_accel * (max_acceleration / accel_magnitude)
    
    return velocity + desired_accel * dt


def create_rotation_matrix(yaw: float, pitch: float, roll: float) -> np.ndarray:
    """Create 3D rotation matrix from Euler angles"""
    # Rotation around z-axis (yaw)
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    
    # Rotation around y-axis (pitch)
    Ry = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    
    # Rotation around x-axis (roll)
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    
    return Rz @ Ry @ Rx
