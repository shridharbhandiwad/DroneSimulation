"""
Physics-based drone trajectory generator
Generates realistic trajectories given initial conditions and waypoints
"""
import numpy as np
from typing import List, Dict, Tuple
from utils import normalize_vector, distance_3d, limit_acceleration


class DronePhysics:
    """Physical model of drone dynamics"""
    
    def __init__(self, max_speed: float = 15.0, max_acceleration: float = 5.0,
                 max_vertical_speed: float = 5.0):
        """
        Args:
            max_speed: Maximum horizontal speed (m/s)
            max_acceleration: Maximum acceleration (m/s^2)
            max_vertical_speed: Maximum vertical speed (m/s)
        """
        self.max_speed = max_speed
        self.max_acceleration = max_acceleration
        self.max_vertical_speed = max_vertical_speed
        self.drag_coefficient = 0.1
        
    def update(self, state: Dict, target_waypoint: np.ndarray, dt: float) -> Dict:
        """
        Update drone state for one timestep
        
        Args:
            state: Current state dict with 'position', 'velocity', 'acceleration'
            target_waypoint: Target position to move towards
            dt: Time step in seconds
            
        Returns:
            Updated state dict
        """
        position = state['position']
        velocity = state['velocity']
        
        # Calculate desired direction
        to_target = target_waypoint - position
        distance = np.linalg.norm(to_target)
        
        if distance < 0.1:  # Reached waypoint
            target_velocity = np.zeros(3)
        else:
            direction = to_target / distance
            
            # Desired speed based on distance (slow down near target)
            desired_speed = min(self.max_speed, distance / 2.0)
            target_velocity = direction * desired_speed
            
            # Limit vertical speed
            target_velocity[2] = np.clip(target_velocity[2], 
                                         -self.max_vertical_speed, 
                                         self.max_vertical_speed)
        
        # Apply acceleration limits
        velocity_change = target_velocity - velocity
        max_change = self.max_acceleration * dt
        if np.linalg.norm(velocity_change) > max_change:
            velocity_change = normalize_vector(velocity_change) * max_change
        
        new_velocity = velocity + velocity_change
        
        # Apply drag
        drag = -self.drag_coefficient * new_velocity * np.linalg.norm(new_velocity)
        new_velocity += drag * dt
        
        # Calculate acceleration
        acceleration = (new_velocity - velocity) / dt
        
        # Update position
        new_position = position + new_velocity * dt + 0.5 * acceleration * dt**2
        
        return {
            'position': new_position,
            'velocity': new_velocity,
            'acceleration': acceleration,
            'time': state['time'] + dt
        }


class TrajectoryGenerator:
    """Generate complete drone trajectories"""
    
    def __init__(self, dt: float = 0.1):
        """
        Args:
            dt: Time step in seconds (default 100ms)
        """
        self.dt = dt
        self.physics = DronePhysics()
        
    def generate(self, initial_position: np.ndarray, initial_velocity: np.ndarray,
                 waypoints: List[np.ndarray], max_time: float = 60.0) -> Dict:
        """
        Generate complete trajectory
        
        Args:
            initial_position: Starting position [x, y, z]
            initial_velocity: Starting velocity [vx, vy, vz]
            waypoints: List of waypoint positions to visit
            max_time: Maximum simulation time in seconds
            
        Returns:
            Dict with trajectory data including positions, velocities, accelerations, times
        """
        state = {
            'position': np.array(initial_position, dtype=np.float32),
            'velocity': np.array(initial_velocity, dtype=np.float32),
            'acceleration': np.zeros(3, dtype=np.float32),
            'time': 0.0
        }
        
        # Storage for trajectory
        positions = [state['position'].copy()]
        velocities = [state['velocity'].copy()]
        accelerations = [state['acceleration'].copy()]
        times = [state['time']]
        current_waypoint_idx = [0]
        
        current_wp_idx = 0
        max_steps = int(max_time / self.dt)
        
        for step in range(max_steps):
            # Get current target waypoint
            if current_wp_idx < len(waypoints):
                target = np.array(waypoints[current_wp_idx])
                
                # Check if reached current waypoint
                if distance_3d(state['position'], target) < 0.5:
                    current_wp_idx += 1
                    if current_wp_idx >= len(waypoints):
                        # Reached all waypoints
                        break
                    target = np.array(waypoints[current_wp_idx])
            else:
                break
            
            # Update physics
            state = self.physics.update(state, target, self.dt)
            
            # Store data
            positions.append(state['position'].copy())
            velocities.append(state['velocity'].copy())
            accelerations.append(state['acceleration'].copy())
            times.append(state['time'])
            current_waypoint_idx.append(current_wp_idx)
            
            # Early termination if stationary at final waypoint
            if (current_wp_idx >= len(waypoints) - 1 and 
                np.linalg.norm(state['velocity']) < 0.1):
                break
        
        return {
            'positions': np.array(positions),
            'velocities': np.array(velocities),
            'accelerations': np.array(accelerations),
            'times': np.array(times),
            'waypoint_indices': np.array(current_waypoint_idx),
            'waypoints': np.array(waypoints),
            'dt': self.dt
        }
    
    def add_noise(self, trajectory: Dict, position_noise: float = 0.1,
                  velocity_noise: float = 0.05) -> Dict:
        """Add realistic noise to trajectory for training data augmentation"""
        noisy_traj = trajectory.copy()
        
        pos_noise = np.random.normal(0, position_noise, trajectory['positions'].shape)
        vel_noise = np.random.normal(0, velocity_noise, trajectory['velocities'].shape)
        
        noisy_traj['positions'] = trajectory['positions'] + pos_noise
        noisy_traj['velocities'] = trajectory['velocities'] + vel_noise
        
        return noisy_traj
