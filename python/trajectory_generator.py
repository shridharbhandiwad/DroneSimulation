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
        
    def update(self, state: Dict, target_waypoint: np.ndarray, target_speed: float, dt: float) -> Dict:
        """
        Update drone state for one timestep
        
        Args:
            state: Current state dict with 'position', 'velocity', 'acceleration'
            target_waypoint: Target position to move towards
            target_speed: Desired speed for this waypoint (m/s)
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
            
            # Use waypoint-specific speed, limited by max speed
            # Slow down near target for smooth approach
            slowdown_distance = 3.0  # Start slowing down 3m from target
            if distance < slowdown_distance:
                desired_speed = min(target_speed, distance / slowdown_distance * target_speed)
            else:
                desired_speed = min(target_speed, self.max_speed)
            
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
        self.waypoints = []  # Current waypoints (position, speed tuples)
        self.current_waypoint_idx = 0  # Current waypoint being targeted
        
    def generate(self, initial_position: np.ndarray, initial_velocity: np.ndarray,
                 waypoints: List, max_time: float = 60.0) -> Dict:
        """
        Generate complete trajectory
        
        Args:
            initial_position: Starting position [x, y, z]
            initial_velocity: Starting velocity [vx, vy, vz]
            waypoints: List of waypoints - each can be:
                      - np.ndarray [x, y, z] with default speed 10 m/s
                      - dict {'position': [x,y,z], 'speed': float}
                      - tuple ([x,y,z], speed)
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
        
        # Parse waypoints to extract positions and speeds
        waypoint_positions = []
        waypoint_speeds = []
        
        for wp in waypoints:
            if isinstance(wp, dict):
                # Dict format: {'position': [x,y,z], 'speed': float}
                waypoint_positions.append(np.array(wp['position']))
                waypoint_speeds.append(wp.get('speed', 10.0))
            elif isinstance(wp, tuple) and len(wp) == 2:
                # Tuple format: ([x,y,z], speed)
                waypoint_positions.append(np.array(wp[0]))
                waypoint_speeds.append(wp[1])
            else:
                # Array format: [x,y,z] with default speed
                waypoint_positions.append(np.array(wp))
                waypoint_speeds.append(10.0)  # Default speed
        
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
            if current_wp_idx < len(waypoint_positions):
                target = waypoint_positions[current_wp_idx]
                target_speed = waypoint_speeds[current_wp_idx]
                
                # Check if reached current waypoint
                if distance_3d(state['position'], target) < 0.5:
                    current_wp_idx += 1
                    if current_wp_idx >= len(waypoint_positions):
                        # Reached all waypoints
                        break
                    target = waypoint_positions[current_wp_idx]
                    target_speed = waypoint_speeds[current_wp_idx]
            else:
                break
            
            # Update physics with target speed
            state = self.physics.update(state, target, target_speed, self.dt)
            
            # Store data
            positions.append(state['position'].copy())
            velocities.append(state['velocity'].copy())
            accelerations.append(state['acceleration'].copy())
            times.append(state['time'])
            current_waypoint_idx.append(current_wp_idx)
            
            # Early termination if stationary at final waypoint
            if (current_wp_idx >= len(waypoint_positions) - 1 and 
                np.linalg.norm(state['velocity']) < 0.1):
                break
        
        return {
            'positions': np.array(positions),
            'velocities': np.array(velocities),
            'accelerations': np.array(accelerations),
            'times': np.array(times),
            'waypoint_indices': np.array(current_waypoint_idx),
            'waypoints': np.array(waypoint_positions),
            'waypoint_speeds': np.array(waypoint_speeds),
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
    
    def regenerate_from_current(self, current_position: np.ndarray, 
                                current_velocity: np.ndarray,
                                waypoints: List,
                                current_waypoint_idx: int = 0,
                                max_time: float = 60.0) -> Dict:
        """
        Regenerate trajectory from current position with new or modified waypoints.
        This allows dynamic path modification during flight.
        
        Args:
            current_position: Current position [x, y, z]
            current_velocity: Current velocity [vx, vy, vz]
            waypoints: New list of waypoints to visit (can include speed)
            current_waypoint_idx: Index of waypoint to target first (default: 0)
            max_time: Maximum simulation time in seconds
            
        Returns:
            Dict with trajectory data
        """
        # Filter out waypoints that are too close to current position
        # or already passed
        filtered_waypoints = []
        for i, wp in enumerate(waypoints):
            if i >= current_waypoint_idx:
                filtered_waypoints.append(wp)
        
        # If no waypoints remain, use original list
        if not filtered_waypoints:
            filtered_waypoints = waypoints
        
        # Generate trajectory from current state
        return self.generate(current_position, current_velocity, 
                           filtered_waypoints, max_time)
    
    def add_waypoint_at_index(self, waypoint: np.ndarray, index: int = -1):
        """
        Add a waypoint at a specific index
        
        Args:
            waypoint: New waypoint position [x, y, z]
            index: Index to insert at (-1 for append)
        """
        if index == -1 or index >= len(self.waypoints):
            self.waypoints.append(np.array(waypoint))
        else:
            self.waypoints.insert(index, np.array(waypoint))
    
    def remove_waypoint(self, index: int):
        """
        Remove a waypoint at a specific index
        
        Args:
            index: Index of waypoint to remove
        """
        if 0 <= index < len(self.waypoints):
            self.waypoints.pop(index)
    
    def modify_waypoint(self, index: int, new_position: np.ndarray):
        """
        Modify an existing waypoint
        
        Args:
            index: Index of waypoint to modify
            new_position: New position [x, y, z]
        """
        if 0 <= index < len(self.waypoints):
            self.waypoints[index] = np.array(new_position)
    
    def get_waypoints(self) -> List[np.ndarray]:
        """Get current waypoints"""
        return self.waypoints.copy()
    
    def set_waypoints(self, waypoints: List[np.ndarray]):
        """Set waypoints"""
        self.waypoints = [np.array(wp) for wp in waypoints]
        self.current_waypoint_idx = 0
