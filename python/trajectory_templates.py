"""
Pre-defined trajectory templates for common drone flight patterns
"""
import numpy as np
from typing import List, Dict, Tuple


class TrajectoryTemplates:
    """Collection of pre-defined trajectory patterns"""
    
    @staticmethod
    def circle(center: Tuple[float, float, float] = (0, 0, 10),
               radius: float = 20.0,
               num_points: int = 16,
               speed: float = 10.0,
               clockwise: bool = True) -> List[Dict]:
        """
        Generate circular trajectory
        
        Args:
            center: Center point (x, y, z)
            radius: Circle radius in meters
            num_points: Number of waypoints
            speed: Speed at each waypoint (m/s)
            clockwise: Direction of rotation
            
        Returns:
            List of waypoint dicts with 'position' and 'speed'
        """
        waypoints = []
        cx, cy, cz = center
        
        for i in range(num_points):
            angle = 2 * np.pi * i / num_points
            if not clockwise:
                angle = -angle
            
            x = cx + radius * np.cos(angle)
            y = cy + radius * np.sin(angle)
            z = cz
            
            waypoints.append({
                'position': [x, y, z],
                'speed': speed
            })
        
        # Close the circle
        waypoints.append({
            'position': [cx + radius, cy, cz],
            'speed': speed
        })
        
        return waypoints
    
    @staticmethod
    def spiral(center: Tuple[float, float, float] = (0, 0, 5),
               start_radius: float = 5.0,
               end_radius: float = 25.0,
               start_height: float = 5.0,
               end_height: float = 30.0,
               num_turns: float = 3.0,
               num_points: int = 50,
               speed: float = 12.0,
               ascending: bool = True) -> List[Dict]:
        """
        Generate spiral trajectory (ascending or descending)
        
        Args:
            center: Center point (x, y, z_start)
            start_radius: Starting radius in meters
            end_radius: Ending radius in meters
            start_height: Starting height
            end_height: Ending height
            num_turns: Number of complete rotations
            num_points: Number of waypoints
            speed: Speed at each waypoint (m/s)
            ascending: True for ascending spiral, False for descending
            
        Returns:
            List of waypoint dicts
        """
        waypoints = []
        cx, cy, _ = center
        
        if not ascending:
            start_height, end_height = end_height, start_height
            start_radius, end_radius = end_radius, start_radius
        
        for i in range(num_points):
            t = i / (num_points - 1)  # 0 to 1
            
            angle = 2 * np.pi * num_turns * t
            radius = start_radius + (end_radius - start_radius) * t
            height = start_height + (end_height - start_height) * t
            
            x = cx + radius * np.cos(angle)
            y = cy + radius * np.sin(angle)
            z = height
            
            waypoints.append({
                'position': [x, y, z],
                'speed': speed
            })
        
        return waypoints
    
    @staticmethod
    def ascend(start_pos: Tuple[float, float, float] = (0, 0, 2),
               height_change: float = 30.0,
               num_points: int = 10,
               speed: float = 5.0) -> List[Dict]:
        """
        Generate vertical ascent trajectory
        
        Args:
            start_pos: Starting position (x, y, z)
            height_change: Height to ascend in meters
            num_points: Number of waypoints
            speed: Vertical speed (m/s)
            
        Returns:
            List of waypoint dicts
        """
        waypoints = []
        x, y, z = start_pos
        
        for i in range(num_points):
            height = z + height_change * i / (num_points - 1)
            waypoints.append({
                'position': [x, y, height],
                'speed': speed
            })
        
        return waypoints
    
    @staticmethod
    def descend(start_pos: Tuple[float, float, float] = (0, 0, 30),
                height_change: float = 25.0,
                num_points: int = 10,
                speed: float = 4.0) -> List[Dict]:
        """
        Generate vertical descent trajectory
        
        Args:
            start_pos: Starting position (x, y, z)
            height_change: Height to descend in meters (positive value)
            num_points: Number of waypoints
            speed: Vertical speed (m/s)
            
        Returns:
            List of waypoint dicts
        """
        waypoints = []
        x, y, z = start_pos
        
        for i in range(num_points):
            height = z - height_change * i / (num_points - 1)
            waypoints.append({
                'position': [x, y, height],
                'speed': speed
            })
        
        return waypoints
    
    @staticmethod
    def sharp_turn(start_pos: Tuple[float, float, float] = (0, 0, 10),
                   direction: str = 'right',
                   turn_angle: float = 90.0,
                   leg_length: float = 20.0,
                   num_points: int = 8,
                   speed: float = 15.0) -> List[Dict]:
        """
        Generate sharp turn trajectory (L-shape)
        
        Args:
            start_pos: Starting position (x, y, z)
            direction: 'right', 'left', 'up', 'down'
            turn_angle: Angle of turn in degrees
            leg_length: Length of each leg in meters
            num_points: Number of waypoints per leg
            speed: Speed at each waypoint (m/s)
            
        Returns:
            List of waypoint dicts
        """
        waypoints = []
        x, y, z = start_pos
        
        # First leg - straight ahead (along X)
        for i in range(num_points):
            t = i / (num_points - 1)
            waypoints.append({
                'position': [x + leg_length * t, y, z],
                'speed': speed
            })
        
        # Turn point
        turn_x = x + leg_length
        angle_rad = np.radians(turn_angle)
        
        # Second leg - after turn
        for i in range(1, num_points):
            t = i / (num_points - 1)
            
            if direction == 'right':
                new_x = turn_x
                new_y = y + leg_length * t
            elif direction == 'left':
                new_x = turn_x
                new_y = y - leg_length * t
            elif direction == 'up':
                new_x = turn_x + leg_length * t * np.cos(angle_rad)
                new_y = y
                z = z + leg_length * t * np.sin(angle_rad)
            else:  # down
                new_x = turn_x + leg_length * t * np.cos(angle_rad)
                new_y = y
                z = z - leg_length * t * np.sin(angle_rad)
            
            waypoints.append({
                'position': [new_x if direction in ['right', 'left', 'up', 'down'] else turn_x,
                           new_y if direction in ['right', 'left'] else y,
                           z],
                'speed': speed
            })
        
        return waypoints
    
    @staticmethod
    def s_curve(start_pos: Tuple[float, float, float] = (0, 0, 10),
                length: float = 40.0,
                amplitude: float = 15.0,
                num_waves: float = 2.0,
                num_points: int = 30,
                speed: float = 12.0,
                axis: str = 'xy') -> List[Dict]:
        """
        Generate S-curve (sinusoidal) trajectory
        
        Args:
            start_pos: Starting position (x, y, z)
            length: Total length along primary axis in meters
            amplitude: Amplitude of sine wave in meters
            num_waves: Number of complete wave cycles
            num_points: Number of waypoints
            speed: Speed at each waypoint (m/s)
            axis: 'xy' (horizontal), 'xz' (vertical), or 'yz'
            
        Returns:
            List of waypoint dicts
        """
        waypoints = []
        x, y, z = start_pos
        
        for i in range(num_points):
            t = i / (num_points - 1)
            
            # Sinusoidal offset
            offset = amplitude * np.sin(2 * np.pi * num_waves * t)
            
            if axis == 'xy':
                new_x = x + length * t
                new_y = y + offset
                new_z = z
            elif axis == 'xz':
                new_x = x + length * t
                new_y = y
                new_z = z + offset
            else:  # yz
                new_x = x
                new_y = y + length * t
                new_z = z + offset
            
            waypoints.append({
                'position': [new_x, new_y, new_z],
                'speed': speed
            })
        
        return waypoints
    
    @staticmethod
    def c_curve(start_pos: Tuple[float, float, float] = (0, 0, 10),
                radius: float = 20.0,
                arc_angle: float = 180.0,
                num_points: int = 20,
                speed: float = 10.0,
                plane: str = 'xy') -> List[Dict]:
        """
        Generate C-curve (partial circle) trajectory
        
        Args:
            start_pos: Starting position (x, y, z)
            radius: Radius of curve in meters
            arc_angle: Angle of arc in degrees (< 360)
            num_points: Number of waypoints
            speed: Speed at each waypoint (m/s)
            plane: 'xy' (horizontal), 'xz' (vertical forward), or 'yz' (vertical side)
            
        Returns:
            List of waypoint dicts
        """
        waypoints = []
        x, y, z = start_pos
        
        # Start angle at -90 degrees to begin at start_pos
        start_angle = -np.pi / 2
        arc_rad = np.radians(arc_angle)
        
        for i in range(num_points):
            t = i / (num_points - 1)
            angle = start_angle + arc_rad * t
            
            if plane == 'xy':
                # Horizontal C-curve
                new_x = x + radius * np.cos(angle)
                new_y = y + radius + radius * np.sin(angle)
                new_z = z
            elif plane == 'xz':
                # Vertical C-curve (forward)
                new_x = x + radius * np.cos(angle)
                new_y = y
                new_z = z + radius + radius * np.sin(angle)
            else:  # yz
                # Vertical C-curve (sideways)
                new_x = x
                new_y = y + radius * np.cos(angle)
                new_z = z + radius + radius * np.sin(angle)
            
            waypoints.append({
                'position': [new_x, new_y, new_z],
                'speed': speed
            })
        
        return waypoints
    
    @staticmethod
    def figure_eight(center: Tuple[float, float, float] = (0, 0, 15),
                     radius: float = 15.0,
                     num_points: int = 40,
                     speed: float = 12.0,
                     plane: str = 'xy') -> List[Dict]:
        """
        Generate figure-eight trajectory
        
        Args:
            center: Center point (x, y, z)
            radius: Radius of each loop in meters
            num_points: Number of waypoints
            speed: Speed at each waypoint (m/s)
            plane: 'xy' (horizontal) or 'xz' (vertical)
            
        Returns:
            List of waypoint dicts
        """
        waypoints = []
        cx, cy, cz = center
        
        for i in range(num_points):
            t = 2 * np.pi * i / (num_points - 1)
            
            # Lemniscate of Gerono (figure-eight curve)
            # x = a * cos(t)
            # y = a * sin(t) * cos(t)
            
            if plane == 'xy':
                x = cx + radius * np.cos(t)
                y = cy + radius * np.sin(t) * np.cos(t)
                z = cz
            else:  # xz
                x = cx + radius * np.cos(t)
                y = cy
                z = cz + radius * np.sin(t) * np.cos(t)
            
            waypoints.append({
                'position': [x, y, z],
                'speed': speed
            })
        
        # Close the loop
        waypoints.append(waypoints[0])
        
        return waypoints
    
    @staticmethod
    def square(center: Tuple[float, float, float] = (0, 0, 10),
               side_length: float = 30.0,
               num_points_per_side: int = 8,
               speed: float = 10.0) -> List[Dict]:
        """
        Generate square trajectory
        
        Args:
            center: Center point (x, y, z)
            side_length: Length of each side in meters
            num_points_per_side: Number of waypoints per side
            speed: Speed at each waypoint (m/s)
            
        Returns:
            List of waypoint dicts
        """
        waypoints = []
        cx, cy, cz = center
        half = side_length / 2
        
        # Define corners
        corners = [
            (cx - half, cy - half, cz),  # Bottom-left
            (cx + half, cy - half, cz),  # Bottom-right
            (cx + half, cy + half, cz),  # Top-right
            (cx - half, cy + half, cz),  # Top-left
        ]
        
        # Generate points along each edge
        for i in range(4):
            start = corners[i]
            end = corners[(i + 1) % 4]
            
            for j in range(num_points_per_side):
                t = j / num_points_per_side
                x = start[0] + (end[0] - start[0]) * t
                y = start[1] + (end[1] - start[1]) * t
                z = cz
                
                waypoints.append({
                    'position': [x, y, z],
                    'speed': speed
                })
        
        # Close the square
        waypoints.append({
            'position': list(corners[0]),
            'speed': speed
        })
        
        return waypoints
    
    @staticmethod
    def get_template_list() -> List[str]:
        """Get list of available template names"""
        return [
            'circle',
            'spiral_ascending',
            'spiral_descending',
            'ascend',
            'descend',
            'sharp_turn_right',
            'sharp_turn_left',
            's_curve_horizontal',
            's_curve_vertical',
            'c_curve_horizontal',
            'c_curve_vertical',
            'figure_eight',
            'square'
        ]
    
    @staticmethod
    def get_template(name: str, **kwargs) -> List[Dict]:
        """
        Get a template by name with optional parameters
        
        Args:
            name: Template name
            **kwargs: Template-specific parameters
            
        Returns:
            List of waypoint dicts
        """
        templates = {
            'circle': lambda: TrajectoryTemplates.circle(**kwargs),
            'spiral_ascending': lambda: TrajectoryTemplates.spiral(ascending=True, **kwargs),
            'spiral_descending': lambda: TrajectoryTemplates.spiral(ascending=False, **kwargs),
            'ascend': lambda: TrajectoryTemplates.ascend(**kwargs),
            'descend': lambda: TrajectoryTemplates.descend(**kwargs),
            'sharp_turn_right': lambda: TrajectoryTemplates.sharp_turn(direction='right', **kwargs),
            'sharp_turn_left': lambda: TrajectoryTemplates.sharp_turn(direction='left', **kwargs),
            's_curve_horizontal': lambda: TrajectoryTemplates.s_curve(axis='xy', **kwargs),
            's_curve_vertical': lambda: TrajectoryTemplates.s_curve(axis='xz', **kwargs),
            'c_curve_horizontal': lambda: TrajectoryTemplates.c_curve(plane='xy', **kwargs),
            'c_curve_vertical': lambda: TrajectoryTemplates.c_curve(plane='xz', **kwargs),
            'figure_eight': lambda: TrajectoryTemplates.figure_eight(**kwargs),
            'square': lambda: TrajectoryTemplates.square(**kwargs)
        }
        
        if name not in templates:
            raise ValueError(f"Unknown template: {name}. Available: {', '.join(templates.keys())}")
        
        return templates[name]()
