"""
PyQt5-based 3D simulation with camera feed visualization
"""
import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, QGroupBox,
                             QGridLayout, QLineEdit, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import cv2
from trajectory_generator import TrajectoryGenerator
from ml_model import TrajectoryPredictor
import os


class CameraSimulator:
    """Simulate camera feed from drone perspective"""
    
    def __init__(self, width=640, height=480):
        self.width = width
        self.height = height
        
    def generate_ground_texture(self):
        """Generate a textured ground for visualization"""
        # Create a grid pattern
        grid = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        grid_size = 50
        
        for i in range(0, self.height, grid_size):
            cv2.line(grid, (0, i), (self.width, i), (100, 100, 100), 1)
        for j in range(0, self.width, grid_size):
            cv2.line(grid, (j, 0), (j, self.height), (100, 100, 100), 1)
        
        return grid
    
    def render_camera_view(self, position, yaw, pitch, ground_height=0):
        """
        Render camera view from drone
        
        Args:
            position: Drone position [x, y, z]
            yaw: Yaw angle in radians
            pitch: Pitch angle in radians
            ground_height: Height of ground
        
        Returns:
            Camera image as numpy array
        """
        # Create base frame
        frame = self.generate_ground_texture()
        
        # Add horizon line based on pitch
        horizon_y = int(self.height / 2 - pitch * 100)
        horizon_y = np.clip(horizon_y, 0, self.height)
        
        # Sky (blue gradient)
        frame[:horizon_y] = [135, 206, 235]  # Sky blue
        
        # Ground (green with grid)
        if horizon_y < self.height:
            ground = np.zeros((self.height - horizon_y, self.width, 3), dtype=np.uint8)
            ground[:, :] = [34, 139, 34]  # Forest green
            
            # Add grid pattern
            grid_size = max(10, int(50 - position[2]))
            for i in range(0, self.height - horizon_y, grid_size):
                cv2.line(ground, (0, i), (self.width, i), (50, 150, 50), 1)
            
            frame[horizon_y:] = ground
        
        # Add telemetry overlay
        altitude = position[2] - ground_height
        
        # Add HUD elements
        cv2.putText(frame, f"ALT: {altitude:.1f}m", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"POS: ({position[0]:.1f}, {position[1]:.1f})", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"YAW: {np.degrees(yaw):.1f}deg", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"PITCH: {np.degrees(pitch):.1f}deg", (10, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add crosshair
        center_x, center_y = self.width // 2, self.height // 2
        cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), 
                (0, 255, 0), 2)
        cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), 
                (0, 255, 0), 2)
        cv2.circle(frame, (center_x, center_y), 30, (0, 255, 0), 2)
        
        return frame


class DroneSimulationWindow(QMainWindow):
    """Main simulation window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Trajectory Simulation")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize components
        self.trajectory_generator = TrajectoryGenerator(dt=0.1)
        self.camera_sim = CameraSimulator()
        
        # Try to load ML model if available
        self.use_ml = False
        model_path = '../models/best_model.pth'
        if os.path.exists(model_path):
            try:
                self.predictor = TrajectoryPredictor(model_path)
                self.use_ml = True
                print("ML model loaded successfully")
            except Exception as e:
                print(f"Could not load ML model: {e}")
        
        # Simulation state
        self.current_trajectory = None
        self.current_step = 0
        self.is_playing = False
        self.playback_speed = 1.0
        
        # Setup UI
        self.setup_ui()
        
        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        
        # Generate initial trajectory
        self.generate_new_trajectory()
        
    def setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel - 3D visualization
        left_panel = QVBoxLayout()
        
        # 3D plot
        self.plot_widget = gl.GLViewWidget()
        self.plot_widget.setMinimumSize(700, 600)
        self.plot_widget.setCameraPosition(distance=100)
        left_panel.addWidget(self.plot_widget)
        
        # Initialize 3D scene
        self.setup_3d_scene()
        
        # Playback controls
        control_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)
        control_layout.addWidget(self.play_btn)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_simulation)
        control_layout.addWidget(self.reset_btn)
        
        self.new_traj_btn = QPushButton("New Trajectory")
        self.new_traj_btn.clicked.connect(self.generate_new_trajectory)
        control_layout.addWidget(self.new_traj_btn)
        
        control_layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(50)
        self.speed_slider.setValue(10)
        self.speed_slider.valueChanged.connect(self.update_speed)
        control_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("1.0x")
        control_layout.addWidget(self.speed_label)
        
        left_panel.addLayout(control_layout)
        
        # Right panel - Camera feed and info
        right_panel = QVBoxLayout()
        
        # Camera feed
        camera_group = QGroupBox("Camera Feed")
        camera_layout = QVBoxLayout()
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setScaledContents(True)
        camera_layout.addWidget(self.camera_label)
        camera_group.setLayout(camera_layout)
        right_panel.addWidget(camera_group)
        
        # Info panel
        info_group = QGroupBox("Telemetry")
        info_layout = QGridLayout()
        
        self.info_labels = {}
        info_items = [
            ("Position", "position"),
            ("Velocity", "velocity"),
            ("Acceleration", "acceleration"),
            ("Current Waypoint", "waypoint"),
            ("Time", "time"),
            ("Progress", "progress")
        ]
        
        for i, (label, key) in enumerate(info_items):
            info_layout.addWidget(QLabel(f"{label}:"), i, 0)
            value_label = QLabel("N/A")
            self.info_labels[key] = value_label
            info_layout.addWidget(value_label, i, 1)
        
        info_group.setLayout(info_layout)
        right_panel.addWidget(info_group)
        
        # Add ML status
        ml_status = QLabel(f"ML Model: {'Enabled' if self.use_ml else 'Disabled (Physics Only)'}")
        ml_status.setStyleSheet("color: green" if self.use_ml else "color: orange")
        right_panel.addWidget(ml_status)
        
        right_panel.addStretch()
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)
    
    def setup_3d_scene(self):
        """Setup 3D visualization scene"""
        # Grid
        grid = gl.GLGridItem()
        grid.scale(2, 2, 1)
        self.plot_widget.addItem(grid)
        
        # Trajectory line
        self.trajectory_line = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0, 1, 0, 1),
            width=2
        )
        self.plot_widget.addItem(self.trajectory_line)
        
        # Drone marker
        self.drone_marker = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 5]]),
            color=(1, 0, 0, 1),
            size=10
        )
        self.plot_widget.addItem(self.drone_marker)
        
        # Waypoint markers
        self.waypoint_markers = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0, 0, 1, 1),
            size=8
        )
        self.plot_widget.addItem(self.waypoint_markers)
    
    def generate_new_trajectory(self):
        """Generate a new random trajectory"""
        # Random initial conditions
        initial_pos = np.array([0, 0, 5])
        initial_vel = np.array([0, 0, 0])
        
        # Random waypoints
        num_waypoints = np.random.randint(3, 6)
        waypoints = []
        for _ in range(num_waypoints):
            wp = np.array([
                np.random.uniform(-30, 30),
                np.random.uniform(-30, 30),
                np.random.uniform(5, 20)
            ])
            waypoints.append(wp)
        
        # Generate trajectory
        self.current_trajectory = self.trajectory_generator.generate(
            initial_pos, initial_vel, waypoints
        )
        
        # Update visualization
        self.update_3d_scene()
        self.reset_simulation()
    
    def update_3d_scene(self):
        """Update 3D scene with current trajectory"""
        if self.current_trajectory is None:
            return
        
        # Update trajectory line
        positions = self.current_trajectory['positions']
        self.trajectory_line.setData(pos=positions)
        
        # Update waypoint markers
        waypoints = self.current_trajectory['waypoints']
        self.waypoint_markers.setData(pos=waypoints)
    
    def toggle_play(self):
        """Toggle play/pause"""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_btn.setText("Pause")
            self.timer.start(int(100 / self.playback_speed))  # 100ms base
        else:
            self.play_btn.setText("Play")
            self.timer.stop()
    
    def reset_simulation(self):
        """Reset simulation to start"""
        self.current_step = 0
        self.is_playing = False
        self.play_btn.setText("Play")
        self.timer.stop()
        self.update_visualization()
    
    def update_speed(self, value):
        """Update playback speed"""
        self.playback_speed = value / 10.0
        self.speed_label.setText(f"{self.playback_speed:.1f}x")
        
        if self.is_playing:
            self.timer.setInterval(int(100 / self.playback_speed))
    
    def update_simulation(self):
        """Update simulation by one step"""
        if self.current_trajectory is None:
            return
        
        self.current_step += 1
        
        if self.current_step >= len(self.current_trajectory['positions']):
            self.current_step = len(self.current_trajectory['positions']) - 1
            self.is_playing = False
            self.play_btn.setText("Play")
            self.timer.stop()
        
        self.update_visualization()
    
    def update_visualization(self):
        """Update all visualizations"""
        if self.current_trajectory is None:
            return
        
        positions = self.current_trajectory['positions']
        velocities = self.current_trajectory['velocities']
        accelerations = self.current_trajectory['accelerations']
        times = self.current_trajectory['times']
        waypoints = self.current_trajectory['waypoints']
        wp_indices = self.current_trajectory['waypoint_indices']
        
        # Get current state
        pos = positions[self.current_step]
        vel = velocities[self.current_step]
        acc = accelerations[self.current_step]
        time = times[self.current_step]
        wp_idx = min(wp_indices[self.current_step], len(waypoints) - 1)
        current_wp = waypoints[wp_idx]
        
        # Update drone marker
        self.drone_marker.setData(pos=np.array([pos]))
        
        # Update info labels
        self.info_labels['position'].setText(
            f"({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})"
        )
        self.info_labels['velocity'].setText(
            f"({vel[0]:.2f}, {vel[1]:.2f}, {vel[2]:.2f}) m/s"
        )
        self.info_labels['acceleration'].setText(
            f"({acc[0]:.2f}, {acc[1]:.2f}, {acc[2]:.2f}) m/s²"
        )
        self.info_labels['waypoint'].setText(
            f"#{wp_idx+1} ({current_wp[0]:.1f}, {current_wp[1]:.1f}, {current_wp[2]:.1f})"
        )
        self.info_labels['time'].setText(f"{time:.1f}s")
        self.info_labels['progress'].setText(
            f"{self.current_step}/{len(positions)-1} "
            f"({100*self.current_step/(len(positions)-1):.1f}%)"
        )
        
        # Update camera view
        # Calculate heading to target
        direction = current_wp - pos
        yaw = np.arctan2(direction[1], direction[0])
        horizontal_dist = np.sqrt(direction[0]**2 + direction[1]**2)
        pitch = np.arctan2(direction[2], horizontal_dist)
        
        camera_frame = self.camera_sim.render_camera_view(pos, yaw, pitch)
        
        # Convert to QPixmap
        height, width, channel = camera_frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(camera_frame.data, width, height, bytes_per_line, 
                        QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_image)
        self.camera_label.setPixmap(pixmap)


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = DroneSimulationWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
