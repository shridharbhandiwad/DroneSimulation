"""
PyQt5-based 3D simulation with camera feed visualization
"""
import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, QGroupBox,
                             QGridLayout, QLineEdit, QMessageBox, QListWidget, 
                             QListWidgetItem, QSplitter, QFrame, QCheckBox)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QPalette
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
        self.setWindowTitle("Drone Trajectory Simulation Pro")
        self.setGeometry(100, 100, 1600, 900)
        
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
        
        # Waypoint management
        self.user_waypoints = []
        self.click_mode_enabled = False
        self.click_height = 10.0  # Default height for clicked waypoints
        self.dynamic_mode_enabled = False  # Allow waypoint changes during flight
        
        # Setup UI
        self.setup_ui()
        self.apply_stylesheet()
        
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
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Left panel - 3D visualization and controls
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        
        # Title for 3D view
        view_title = QLabel("🚁 3D Trajectory View")
        view_title.setFont(QFont("Arial", 14, QFont.Bold))
        view_title.setStyleSheet("color: #2c3e50; padding: 5px;")
        left_panel.addWidget(view_title)
        
        # 3D plot
        self.plot_widget = gl.GLViewWidget()
        self.plot_widget.setMinimumSize(800, 550)
        self.plot_widget.setCameraPosition(distance=100)
        self.plot_widget.setObjectName("plot3d")
        left_panel.addWidget(self.plot_widget)
        
        # Initialize 3D scene
        self.setup_3d_scene()
        
        # Playback controls group
        control_group = QGroupBox("⚙️ Simulation Controls")
        control_group.setFont(QFont("Arial", 10, QFont.Bold))
        control_layout = QGridLayout()
        control_layout.setSpacing(10)
        
        self.play_btn = QPushButton("▶️ Play")
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setMinimumHeight(40)
        self.play_btn.setObjectName("playButton")
        control_layout.addWidget(self.play_btn, 0, 0)
        
        self.reset_btn = QPushButton("🔄 Reset")
        self.reset_btn.clicked.connect(self.reset_simulation)
        self.reset_btn.setMinimumHeight(40)
        self.reset_btn.setObjectName("resetButton")
        control_layout.addWidget(self.reset_btn, 0, 1)
        
        self.new_traj_btn = QPushButton("🎲 Random Trajectory")
        self.new_traj_btn.clicked.connect(self.generate_new_trajectory)
        self.new_traj_btn.setMinimumHeight(40)
        self.new_traj_btn.setObjectName("newTrajButton")
        control_layout.addWidget(self.new_traj_btn, 0, 2)
        
        speed_label = QLabel("Speed:")
        speed_label.setStyleSheet("font-weight: bold;")
        control_layout.addWidget(speed_label, 1, 0)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(50)
        self.speed_slider.setValue(10)
        self.speed_slider.valueChanged.connect(self.update_speed)
        control_layout.addWidget(self.speed_slider, 1, 1)
        
        self.speed_label = QLabel("1.0x")
        self.speed_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        control_layout.addWidget(self.speed_label, 1, 2)
        
        control_group.setLayout(control_layout)
        left_panel.addWidget(control_group)
        
        # Middle panel - Waypoint management
        middle_panel = QVBoxLayout()
        middle_panel.setSpacing(10)
        
        # Waypoint controls
        waypoint_group = QGroupBox("📍 Waypoint Manager")
        waypoint_group.setFont(QFont("Arial", 10, QFont.Bold))
        waypoint_layout = QVBoxLayout()
        waypoint_layout.setSpacing(10)
        
        # Click mode toggle
        click_mode_layout = QHBoxLayout()
        self.click_mode_checkbox = QCheckBox("Click to Add Waypoints")
        self.click_mode_checkbox.setFont(QFont("Arial", 9, QFont.Bold))
        self.click_mode_checkbox.stateChanged.connect(self.toggle_click_mode)
        click_mode_layout.addWidget(self.click_mode_checkbox)
        waypoint_layout.addLayout(click_mode_layout)
        
        # Height control for clicked waypoints
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Click Height (m):"))
        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setMinimum(5)
        self.height_slider.setMaximum(30)
        self.height_slider.setValue(10)
        self.height_slider.valueChanged.connect(self.update_click_height)
        height_layout.addWidget(self.height_slider)
        self.height_label = QLabel("10m")
        self.height_label.setStyleSheet("font-weight: bold; color: #2980b9;")
        height_layout.addWidget(self.height_label)
        waypoint_layout.addLayout(height_layout)
        
        # Waypoint list
        list_label = QLabel("Waypoints:")
        list_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        waypoint_layout.addWidget(list_label)
        
        self.waypoint_list = QListWidget()
        self.waypoint_list.setMaximumHeight(200)
        self.waypoint_list.setObjectName("waypointList")
        waypoint_layout.addWidget(self.waypoint_list)
        
        # Waypoint action buttons
        wp_btn_layout = QHBoxLayout()
        
        self.remove_wp_btn = QPushButton("➖ Remove")
        self.remove_wp_btn.clicked.connect(self.remove_selected_waypoint)
        wp_btn_layout.addWidget(self.remove_wp_btn)
        
        self.clear_wp_btn = QPushButton("🗑️ Clear All")
        self.clear_wp_btn.clicked.connect(self.clear_waypoints)
        wp_btn_layout.addWidget(self.clear_wp_btn)
        
        waypoint_layout.addLayout(wp_btn_layout)
        
        # Generate/Apply buttons layout
        gen_btn_layout = QVBoxLayout()
        
        self.generate_traj_btn = QPushButton("✨ Generate Trajectory")
        self.generate_traj_btn.clicked.connect(self.generate_from_waypoints)
        self.generate_traj_btn.setObjectName("generateButton")
        self.generate_traj_btn.setMinimumHeight(35)
        gen_btn_layout.addWidget(self.generate_traj_btn)
        
        # Dynamic waypoint mode toggle
        self.dynamic_mode_checkbox = QCheckBox("🔄 Enable Dynamic Waypoint Mode")
        self.dynamic_mode_checkbox.setFont(QFont("Arial", 9, QFont.Bold))
        self.dynamic_mode_checkbox.setStyleSheet("color: #e74c3c; margin-top: 5px;")
        self.dynamic_mode_checkbox.stateChanged.connect(self.toggle_dynamic_mode)
        gen_btn_layout.addWidget(self.dynamic_mode_checkbox)
        
        # Apply changes during flight button
        self.apply_changes_btn = QPushButton("⚡ Apply Waypoint Changes")
        self.apply_changes_btn.clicked.connect(self.apply_waypoint_changes)
        self.apply_changes_btn.setObjectName("applyButton")
        self.apply_changes_btn.setMinimumHeight(35)
        self.apply_changes_btn.setEnabled(False)
        gen_btn_layout.addWidget(self.apply_changes_btn)
        
        waypoint_layout.addLayout(gen_btn_layout)
        waypoint_group.setLayout(waypoint_layout)
        middle_panel.addWidget(waypoint_group)
        
        # Info panel
        info_group = QGroupBox("📊 Telemetry")
        info_group.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout = QGridLayout()
        info_layout.setSpacing(8)
        
        self.info_labels = {}
        info_items = [
            ("Position", "position"),
            ("Velocity", "velocity"),
            ("Acceleration", "acceleration"),
            ("Current WP", "waypoint"),
            ("Time", "time"),
            ("Progress", "progress")
        ]
        
        for i, (label, key) in enumerate(info_items):
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold; color: #34495e;")
            info_layout.addWidget(label_widget, i, 0)
            value_label = QLabel("N/A")
            value_label.setStyleSheet("color: #16a085;")
            self.info_labels[key] = value_label
            info_layout.addWidget(value_label, i, 1)
        
        info_group.setLayout(info_layout)
        middle_panel.addWidget(info_group)
        
        # ML status
        ml_group = QGroupBox("🤖 AI Status")
        ml_group.setFont(QFont("Arial", 10, QFont.Bold))
        ml_layout = QVBoxLayout()
        ml_status = QLabel(f"{'✓ ML Model Active' if self.use_ml else '⚠ Physics Mode Only'}")
        ml_status.setStyleSheet(
            "color: #27ae60; font-size: 11px; padding: 5px;" if self.use_ml 
            else "color: #f39c12; font-size: 11px; padding: 5px;"
        )
        ml_layout.addWidget(ml_status)
        ml_group.setLayout(ml_layout)
        middle_panel.addWidget(ml_group)
        
        middle_panel.addStretch()
        
        # Right panel - Camera feed
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)
        
        camera_title = QLabel("📹 FPV Camera")
        camera_title.setFont(QFont("Arial", 14, QFont.Bold))
        camera_title.setStyleSheet("color: #2c3e50; padding: 5px;")
        right_panel.addWidget(camera_title)
        
        camera_group = QGroupBox()
        camera_group.setObjectName("cameraGroup")
        camera_layout = QVBoxLayout()
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setScaledContents(True)
        self.camera_label.setStyleSheet("border: 2px solid #34495e; border-radius: 5px;")
        camera_layout.addWidget(self.camera_label)
        camera_group.setLayout(camera_layout)
        right_panel.addWidget(camera_group)
        
        right_panel.addStretch()
        
        # Add panels to main layout
        main_layout.addLayout(left_panel, 3)
        main_layout.addLayout(middle_panel, 1)
        main_layout.addLayout(right_panel, 2)
    
    def apply_stylesheet(self):
        """Apply modern stylesheet to the application"""
        stylesheet = """
            QMainWindow {
                background-color: #ecf0f1;
            }
            
            QGroupBox {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2c3e50;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                font-size: 11px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton#playButton {
                background-color: #27ae60;
            }
            
            QPushButton#playButton:hover {
                background-color: #229954;
            }
            
            QPushButton#resetButton {
                background-color: #e67e22;
            }
            
            QPushButton#resetButton:hover {
                background-color: #d35400;
            }
            
            QPushButton#newTrajButton {
                background-color: #9b59b6;
            }
            
            QPushButton#newTrajButton:hover {
                background-color: #8e44ad;
            }
            
            QPushButton#generateButton {
                background-color: #16a085;
            }
            
            QPushButton#generateButton:hover {
                background-color: #138d75;
            }
            
            QPushButton#applyButton {
                background-color: #e74c3c;
            }
            
            QPushButton#applyButton:hover {
                background-color: #c0392b;
            }
            
            QPushButton#applyButton:disabled {
                background-color: #95a5a6;
            }
            
            QSlider::groove:horizontal {
                border: 1px solid #bdc3c7;
                height: 8px;
                background: #ecf0f1;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: #3498db;
                border: 1px solid #2980b9;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            
            QSlider::handle:horizontal:hover {
                background: #2980b9;
            }
            
            QCheckBox {
                spacing: 5px;
                color: #2c3e50;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #3498db;
            }
            
            QCheckBox::indicator:checked {
                background-color: #3498db;
                image: url(none);
            }
            
            QListWidget {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ffffff;
                padding: 5px;
            }
            
            QListWidget::item {
                padding: 5px;
                border-radius: 3px;
            }
            
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
            
            QLabel {
                color: #2c3e50;
            }
        """
        self.setStyleSheet(stylesheet)
    
    def setup_3d_scene(self):
        """Setup 3D visualization scene"""
        # Grid
        grid = gl.GLGridItem()
        grid.scale(2, 2, 1)
        grid.setColor((100, 100, 100, 100))
        self.plot_widget.addItem(grid)
        
        # Trajectory line
        self.trajectory_line = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.2, 0.8, 0.2, 1),
            width=3,
            antialias=True
        )
        self.plot_widget.addItem(self.trajectory_line)
        
        # Drone marker (larger and more visible)
        self.drone_marker = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 5]]),
            color=(1, 0.2, 0.2, 1),
            size=15,
            pxMode=True
        )
        self.plot_widget.addItem(self.drone_marker)
        
        # Waypoint markers (blue)
        self.waypoint_markers = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.2, 0.4, 1, 1),
            size=12,
            pxMode=True
        )
        self.plot_widget.addItem(self.waypoint_markers)
        
        # User waypoint markers (different color - yellow/gold)
        self.user_waypoint_markers = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(1, 0.8, 0, 1),
            size=14,
            pxMode=True
        )
        self.plot_widget.addItem(self.user_waypoint_markers)
        
        # Connect mouse events
        self.plot_widget.mousePressEvent = self.on_3d_click
    
    def on_3d_click(self, event):
        """Handle clicks on the 3D view to add waypoints"""
        if not self.click_mode_enabled:
            return
        
        # Get the click position
        if event.button() == Qt.LeftButton:
            # Get the position in 3D space
            # We'll project the click onto the ground plane (z = click_height)
            pos = event.pos()
            
            # Use the camera's view matrix to unproject
            # For simplicity, we'll map screen coordinates to world XY plane
            # This is an approximation
            view_width = self.plot_widget.width()
            view_height = self.plot_widget.height()
            
            # Normalize screen coordinates (-1 to 1)
            x_norm = (pos.x() / view_width - 0.5) * 2
            y_norm = -(pos.y() / view_height - 0.5) * 2
            
            # Get camera distance and apply scaling
            camera_dist = self.plot_widget.opts['distance']
            scale = camera_dist / 2.0
            
            # Calculate world position
            x_world = x_norm * scale
            y_world = y_norm * scale
            z_world = self.click_height
            
            waypoint = np.array([x_world, y_world, z_world])
            self.add_waypoint(waypoint)
    
    def toggle_click_mode(self, state):
        """Toggle click-to-add-waypoint mode"""
        self.click_mode_enabled = (state == Qt.Checked)
        
        if self.click_mode_enabled:
            self.plot_widget.setCursor(Qt.CrossCursor)
            self.statusBar().showMessage("Click mode enabled - Click on the 3D view to add waypoints", 3000)
        else:
            self.plot_widget.setCursor(Qt.ArrowCursor)
            self.statusBar().showMessage("Click mode disabled", 2000)
    
    def update_click_height(self, value):
        """Update the height for clicked waypoints"""
        self.click_height = float(value)
        self.height_label.setText(f"{value}m")
    
    def add_waypoint(self, position):
        """Add a waypoint to the list"""
        self.user_waypoints.append(position)
        
        # Update the list widget
        item_text = f"WP {len(self.user_waypoints)}: ({position[0]:.1f}, {position[1]:.1f}, {position[2]:.1f})"
        self.waypoint_list.addItem(item_text)
        
        # Update visualization
        self.update_user_waypoint_markers()
        
        message = f"Added waypoint at ({position[0]:.1f}, {position[1]:.1f}, {position[2]:.1f})"
        
        # If in dynamic mode and trajectory is running, prompt to apply changes
        if self.dynamic_mode_enabled and self.current_trajectory is not None:
            message += " - Click 'Apply Waypoint Changes' to update trajectory"
        
        self.statusBar().showMessage(message, 3000)
    
    def remove_selected_waypoint(self):
        """Remove the selected waypoint from the list"""
        current_row = self.waypoint_list.currentRow()
        if current_row >= 0:
            self.waypoint_list.takeItem(current_row)
            del self.user_waypoints[current_row]
            
            # Update list numbering
            for i in range(self.waypoint_list.count()):
                pos = self.user_waypoints[i]
                self.waypoint_list.item(i).setText(
                    f"WP {i+1}: ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})"
                )
            
            self.update_user_waypoint_markers()
            self.statusBar().showMessage("Waypoint removed", 2000)
    
    def clear_waypoints(self):
        """Clear all waypoints"""
        if self.user_waypoints:
            reply = QMessageBox.question(self, 'Clear Waypoints', 
                                        'Are you sure you want to clear all waypoints?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.user_waypoints.clear()
                self.waypoint_list.clear()
                self.update_user_waypoint_markers()
                self.statusBar().showMessage("All waypoints cleared", 2000)
    
    def update_user_waypoint_markers(self):
        """Update the visual markers for user waypoints"""
        if self.user_waypoints:
            positions = np.array(self.user_waypoints)
            self.user_waypoint_markers.setData(pos=positions)
        else:
            # Hide markers by placing them off-screen
            self.user_waypoint_markers.setData(pos=np.array([[1000, 1000, 1000]]))
    
    def toggle_dynamic_mode(self, state):
        """Toggle dynamic waypoint modification mode"""
        self.dynamic_mode_enabled = (state == Qt.Checked)
        
        if self.dynamic_mode_enabled:
            self.apply_changes_btn.setEnabled(True)
            self.statusBar().showMessage("Dynamic waypoint mode enabled - You can now modify waypoints during flight!", 3000)
        else:
            self.apply_changes_btn.setEnabled(False)
            self.statusBar().showMessage("Dynamic waypoint mode disabled", 2000)
    
    def apply_waypoint_changes(self):
        """Apply waypoint changes during flight - regenerate trajectory from current position"""
        if not self.dynamic_mode_enabled:
            QMessageBox.warning(self, "Dynamic Mode Disabled",
                              "Please enable Dynamic Waypoint Mode first.")
            return
        
        if self.current_trajectory is None:
            QMessageBox.warning(self, "No Active Trajectory",
                              "Please generate a trajectory first.")
            return
        
        if len(self.user_waypoints) < 1:
            QMessageBox.warning(self, "No Waypoints",
                              "Please add at least one waypoint.")
            return
        
        # Get current state
        positions = self.current_trajectory['positions']
        velocities = self.current_trajectory['velocities']
        waypoints = self.current_trajectory['waypoints']
        wp_indices = self.current_trajectory['waypoint_indices']
        
        current_pos = positions[self.current_step]
        current_vel = velocities[self.current_step]
        current_wp_idx = wp_indices[self.current_step]
        
        # Regenerate trajectory from current position with new waypoints
        new_trajectory = self.trajectory_generator.regenerate_from_current(
            current_pos, current_vel, self.user_waypoints.copy(),
            current_waypoint_idx=0  # Start from first waypoint in new list
        )
        
        # Combine old trajectory (up to current point) with new trajectory
        self.current_trajectory['positions'] = np.vstack([
            positions[:self.current_step + 1],
            new_trajectory['positions'][1:]  # Skip first point to avoid duplicate
        ])
        self.current_trajectory['velocities'] = np.vstack([
            velocities[:self.current_step + 1],
            new_trajectory['velocities'][1:]
        ])
        self.current_trajectory['accelerations'] = np.vstack([
            self.current_trajectory['accelerations'][:self.current_step + 1],
            new_trajectory['accelerations'][1:]
        ])
        self.current_trajectory['times'] = np.concatenate([
            self.current_trajectory['times'][:self.current_step + 1],
            new_trajectory['times'][1:] + self.current_trajectory['times'][self.current_step]
        ])
        
        # Update waypoint indices
        old_wp_indices = np.full(self.current_step + 1, current_wp_idx)
        new_wp_indices = new_trajectory['waypoint_indices'][1:]
        self.current_trajectory['waypoint_indices'] = np.concatenate([
            old_wp_indices,
            new_wp_indices
        ])
        
        # Update waypoints
        self.current_trajectory['waypoints'] = np.array(self.user_waypoints)
        
        # Update visualization
        self.update_3d_scene()
        
        self.statusBar().showMessage(
            f"✓ Trajectory updated with {len(self.user_waypoints)} waypoints from current position!", 
            4000
        )
    
    def generate_from_waypoints(self):
        """Generate trajectory from user-defined waypoints"""
        if len(self.user_waypoints) < 1:
            QMessageBox.warning(self, "No Waypoints", 
                              "Please add at least one waypoint before generating trajectory.")
            return
        
        # Initial conditions
        initial_pos = np.array([0, 0, 5])
        initial_vel = np.array([0, 0, 0])
        
        # Generate trajectory
        self.current_trajectory = self.trajectory_generator.generate(
            initial_pos, initial_vel, self.user_waypoints.copy()
        )
        
        # Update visualization
        self.update_3d_scene()
        self.reset_simulation()
        
        self.statusBar().showMessage(f"Generated trajectory with {len(self.user_waypoints)} waypoints", 3000)
    
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
        
        self.statusBar().showMessage("Generated random trajectory", 2000)
    
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
            self.play_btn.setText("⏸️ Pause")
            self.timer.start(int(100 / self.playback_speed))  # 100ms base
            self.statusBar().showMessage("Simulation playing", 2000)
        else:
            self.play_btn.setText("▶️ Play")
            self.timer.stop()
            self.statusBar().showMessage("Simulation paused", 2000)
    
    def reset_simulation(self):
        """Reset simulation to start"""
        self.current_step = 0
        self.is_playing = False
        self.play_btn.setText("▶️ Play")
        self.timer.stop()
        self.update_visualization()
        self.statusBar().showMessage("Simulation reset", 2000)
    
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
            self.play_btn.setText("▶️ Play")
            self.timer.stop()
            self.statusBar().showMessage("Simulation complete", 3000)
        
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
