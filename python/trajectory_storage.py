"""
Trajectory storage and management system for saving and loading trajectories
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np


class TrajectoryStorage:
    """Handle saving and loading of trajectories"""
    
    def __init__(self, storage_dir: str = "saved_trajectories"):
        """
        Initialize trajectory storage
        
        Args:
            storage_dir: Directory to store trajectory files
        """
        self.storage_dir = storage_dir
        self._ensure_storage_dir()
    
    def _ensure_storage_dir(self):
        """Create storage directory if it doesn't exist"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
    
    def save_trajectory(self, waypoints: List[Dict], 
                       name: str,
                       description: str = "",
                       metadata: Optional[Dict] = None) -> str:
        """
        Save trajectory to file
        
        Args:
            waypoints: List of waypoint dicts with 'position' and 'speed'
            name: Name for the trajectory
            description: Optional description
            metadata: Optional metadata dict
            
        Returns:
            Path to saved file
        """
        # Prepare data
        trajectory_data = {
            'name': name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'waypoints': [],
            'metadata': metadata or {}
        }
        
        # Convert waypoints to serializable format
        for wp in waypoints:
            if isinstance(wp, dict):
                # Dict format with position and speed
                pos = wp.get('position', wp)
                if isinstance(pos, np.ndarray):
                    pos = pos.tolist()
                elif isinstance(pos, dict):
                    # Handle nested dict
                    pos = wp.get('position', [0, 0, 0])
                    if isinstance(pos, np.ndarray):
                        pos = pos.tolist()
                
                trajectory_data['waypoints'].append({
                    'position': pos,
                    'speed': wp.get('speed', 10.0)
                })
            elif isinstance(wp, (list, tuple, np.ndarray)):
                # Array format - just position
                pos = np.array(wp).tolist() if isinstance(wp, np.ndarray) else list(wp)
                trajectory_data['waypoints'].append({
                    'position': pos,
                    'speed': 10.0  # Default speed
                })
            else:
                raise ValueError(f"Invalid waypoint format: {type(wp)}")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in name)
        filename = f"{safe_name}_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)
        
        # Save to file
        with open(filepath, 'w') as f:
            json.dump(trajectory_data, f, indent=2)
        
        return filepath
    
    def load_trajectory(self, filepath: str) -> Dict:
        """
        Load trajectory from file
        
        Args:
            filepath: Path to trajectory file
            
        Returns:
            Dict with trajectory data including waypoints
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert positions back to numpy arrays
        for wp in data['waypoints']:
            wp['position'] = np.array(wp['position'])
        
        return data
    
    def list_trajectories(self) -> List[Dict]:
        """
        List all saved trajectories
        
        Returns:
            List of trajectory info dicts with name, description, filepath, created_at
        """
        trajectories = []
        
        if not os.path.exists(self.storage_dir):
            return trajectories
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    trajectories.append({
                        'name': data.get('name', 'Unnamed'),
                        'description': data.get('description', ''),
                        'filepath': filepath,
                        'created_at': data.get('created_at', ''),
                        'num_waypoints': len(data.get('waypoints', []))
                    })
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
        
        # Sort by creation time (newest first)
        trajectories.sort(key=lambda x: x['created_at'], reverse=True)
        
        return trajectories
    
    def delete_trajectory(self, filepath: str) -> bool:
        """
        Delete a saved trajectory
        
        Args:
            filepath: Path to trajectory file
            
        Returns:
            True if deleted successfully
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            print(f"Error deleting trajectory: {e}")
        return False
    
    def export_to_csv(self, filepath: str, output_path: str) -> bool:
        """
        Export trajectory to CSV format
        
        Args:
            filepath: Path to trajectory JSON file
            output_path: Path for output CSV file
            
        Returns:
            True if exported successfully
        """
        try:
            data = self.load_trajectory(filepath)
            
            with open(output_path, 'w') as f:
                # Header
                f.write("waypoint_index,x,y,z,speed\n")
                
                # Waypoints
                for i, wp in enumerate(data['waypoints']):
                    pos = wp['position']
                    speed = wp['speed']
                    f.write(f"{i},{pos[0]},{pos[1]},{pos[2]},{speed}\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def import_from_csv(self, csv_path: str, name: str, description: str = "") -> str:
        """
        Import trajectory from CSV format
        
        Args:
            csv_path: Path to CSV file
            name: Name for the imported trajectory
            description: Optional description
            
        Returns:
            Path to saved trajectory file
        """
        waypoints = []
        
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            
            # Skip header
            for line in lines[1:]:
                parts = line.strip().split(',')
                if len(parts) >= 4:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    speed = float(parts[4]) if len(parts) > 4 else 10.0
                    
                    waypoints.append({
                        'position': [x, y, z],
                        'speed': speed
                    })
        
        return self.save_trajectory(waypoints, name, description)
