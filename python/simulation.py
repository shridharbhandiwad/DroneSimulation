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
        self.setGeometry(100, 100, 1800, 950)
        
        # Initialize components
        self.trajectory_generator = TrajectoryGenerator(dt=0.1)
        # Camera disabled - uncomment below to re-enable
        # self.camera_sim = CameraSimulator()
        
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
        
        # Add status bar
        self.statusBar().showMessage("Ready to simulate drone trajectories", 3000)
        
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
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        # Left panel - 3D visualization and controls
        left_panel = QVBoxLayout()
        left_panel.setSpacing(8)
        
        # Title for 3D view with icon
        view_header = QHBoxLayout()
        view_title = QLabel("3D Trajectory View")
        view_title.setFont(QFont("Arial", 12, QFont.Bold))
        view_title.setStyleSheet("""
            color: #1e3a5f; 
            padding: 8px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #f5f1e8, stop:1 #ffffff);
            border-radius: 6px;
            border-left: 5px solid #d4af37;
        """)
        view_header.addWidget(view_title)
        left_panel.addLayout(view_header)
        
        # 3D plot container with shadow effect
        plot_container = QFrame()
        plot_container.setObjectName("plot3dContainer")
        plot_container.setStyleSheet("""
            #plot3dContainer {
                background: white;
                border-radius: 8px;
                border: 1px solid #d0d0d0;
            }
        """)
        plot_layout = QVBoxLayout(plot_container)
        plot_layout.setContentsMargins(2, 2, 2, 2)
        
        self.plot_widget = gl.GLViewWidget()
        self.plot_widget.setMinimumSize(900, 580)
        self.plot_widget.setCameraPosition(distance=100)
        self.plot_widget.setBackgroundColor('#faf8f3')
        self.plot_widget.setObjectName("plot3d")
        plot_layout.addWidget(self.plot_widget)
        left_panel.addWidget(plot_container)
        
        # Initialize 3D scene
        self.setup_3d_scene()
        
        # Playback controls group
        control_group = QGroupBox("Simulation Controls")
        control_group.setFont(QFont("Arial", 10, QFont.Bold))
        control_layout = QGridLayout()
        control_layout.setSpacing(8)
        control_layout.setContentsMargins(10, 12, 10, 10)
        
        self.play_btn = QPushButton("Play")
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setMinimumHeight(38)
        self.play_btn.setObjectName("playButton")
        control_layout.addWidget(self.play_btn, 0, 0)
        
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.clicked.connect(self.reset_simulation)
        self.reset_btn.setMinimumHeight(38)
        self.reset_btn.setObjectName("resetButton")
        control_layout.addWidget(self.reset_btn, 0, 1)
        
        self.new_traj_btn = QPushButton("Random")
        self.new_traj_btn.clicked.connect(self.generate_new_trajectory)
        self.new_traj_btn.setMinimumHeight(38)
        self.new_traj_btn.setObjectName("newTrajButton")
        control_layout.addWidget(self.new_traj_btn, 0, 2)
        
        speed_label = QLabel("Playback Speed:")
        speed_label.setStyleSheet("font-weight: 600; font-size: 9pt; color: #2c3e50;")
        control_layout.addWidget(speed_label, 1, 0)
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(50)
        self.speed_slider.setValue(10)
        self.speed_slider.valueChanged.connect(self.update_speed)
        control_layout.addWidget(self.speed_slider, 1, 1)
        
        self.speed_label = QLabel("1.0x")
        self.speed_label.setStyleSheet("font-weight: bold; font-size: 9pt; color: #8b6914;")
        control_layout.addWidget(self.speed_label, 1, 2)
        
        control_group.setLayout(control_layout)
        left_panel.addWidget(control_group)
        
        # Middle panel - Waypoint management
        middle_panel = QVBoxLayout()
        middle_panel.setSpacing(8)
        
        # Waypoint controls
        waypoint_group = QGroupBox("Waypoint Manager")
        waypoint_group.setFont(QFont("Arial", 10, QFont.Bold))
        waypoint_layout = QVBoxLayout()
        waypoint_layout.setSpacing(8)
        waypoint_layout.setContentsMargins(10, 12, 10, 10)
        
        # Click mode toggle
        click_mode_layout = QHBoxLayout()
        self.click_mode_checkbox = QCheckBox("Click to Add Waypoints")
        self.click_mode_checkbox.setFont(QFont("Arial", 9))
        self.click_mode_checkbox.stateChanged.connect(self.toggle_click_mode)
        click_mode_layout.addWidget(self.click_mode_checkbox)
        waypoint_layout.addLayout(click_mode_layout)
        
        # Height control for clicked waypoints
        height_layout = QVBoxLayout()
        height_layout.setSpacing(4)
        height_lbl = QLabel("Waypoint Height:")
        height_lbl.setStyleSheet("font-weight: 600; font-size: 9pt; color: #4a4a4a;")
        height_layout.addWidget(height_lbl)
        
        height_control = QHBoxLayout()
        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setMinimum(5)
        self.height_slider.setMaximum(30)
        self.height_slider.setValue(10)
        self.height_slider.valueChanged.connect(self.update_click_height)
        height_control.addWidget(self.height_slider)
        self.height_label = QLabel("10m")
        self.height_label.setStyleSheet("font-weight: bold; font-size: 9pt; color: #8b6914; min-width: 40px;")
        height_control.addWidget(self.height_label)
        height_layout.addLayout(height_control)
        waypoint_layout.addLayout(height_layout)
        
        # Waypoint list
        list_label = QLabel("Active Waypoints:")
        list_label.setStyleSheet("font-weight: 600; font-size: 9pt; margin-top: 6px; color: #4a4a4a;")
        waypoint_layout.addWidget(list_label)
        
        self.waypoint_list = QListWidget()
        self.waypoint_list.setMinimumHeight(160)
        self.waypoint_list.setMaximumHeight(200)
        self.waypoint_list.setObjectName("waypointList")
        waypoint_layout.addWidget(self.waypoint_list)
        
        # Waypoint action buttons
        wp_btn_layout = QHBoxLayout()
        wp_btn_layout.setSpacing(6)
        
        self.remove_wp_btn = QPushButton("Remove")
        self.remove_wp_btn.clicked.connect(self.remove_selected_waypoint)
        self.remove_wp_btn.setMinimumHeight(34)
        self.remove_wp_btn.setObjectName("removeButton")
        wp_btn_layout.addWidget(self.remove_wp_btn)
        
        self.clear_wp_btn = QPushButton("Clear All")
        self.clear_wp_btn.clicked.connect(self.clear_waypoints)
        self.clear_wp_btn.setMinimumHeight(34)
        self.clear_wp_btn.setObjectName("clearButton")
        wp_btn_layout.addWidget(self.clear_wp_btn)
        
        waypoint_layout.addLayout(wp_btn_layout)
        
        # Generate/Apply buttons layout
        gen_btn_layout = QVBoxLayout()
        gen_btn_layout.setSpacing(8)
        
        self.generate_traj_btn = QPushButton("Generate Trajectory")
        self.generate_traj_btn.clicked.connect(self.generate_from_waypoints)
        self.generate_traj_btn.setObjectName("generateButton")
        self.generate_traj_btn.setMinimumHeight(38)
        gen_btn_layout.addWidget(self.generate_traj_btn)
        
        # Dynamic waypoint mode toggle
        self.dynamic_mode_checkbox = QCheckBox("Enable Dynamic Mode")
        self.dynamic_mode_checkbox.setFont(QFont("Arial", 9))
        self.dynamic_mode_checkbox.setStyleSheet("margin-top: 4px;")
        self.dynamic_mode_checkbox.stateChanged.connect(self.toggle_dynamic_mode)
        gen_btn_layout.addWidget(self.dynamic_mode_checkbox)
        
        # Apply changes during flight button
        self.apply_changes_btn = QPushButton("Apply Changes")
        self.apply_changes_btn.clicked.connect(self.apply_waypoint_changes)
        self.apply_changes_btn.setObjectName("applyButton")
        self.apply_changes_btn.setMinimumHeight(38)
        self.apply_changes_btn.setEnabled(False)
        gen_btn_layout.addWidget(self.apply_changes_btn)
        
        waypoint_layout.addLayout(gen_btn_layout)
        waypoint_group.setLayout(waypoint_layout)
        middle_panel.addWidget(waypoint_group)
        
        # Info panel
        info_group = QGroupBox("Flight Telemetry")
        info_group.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout = QGridLayout()
        info_layout.setSpacing(6)
        info_layout.setContentsMargins(10, 12, 10, 10)
        
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
            label_widget.setStyleSheet("font-weight: 600; font-size: 9pt; color: #4a4a4a;")
            info_layout.addWidget(label_widget, i, 0)
            value_label = QLabel("N/A")
            value_label.setStyleSheet("font-size: 9pt; color: #8b6914; font-weight: 600;")
            self.info_labels[key] = value_label
            info_layout.addWidget(value_label, i, 1)
        
        info_group.setLayout(info_layout)
        middle_panel.addWidget(info_group)
        
        # ML status
        ml_group = QGroupBox("AI Status")
        ml_group.setFont(QFont("Arial", 10, QFont.Bold))
        ml_layout = QVBoxLayout()
        ml_layout.setContentsMargins(10, 12, 10, 10)
        ml_status_text = "ML Model Active" if self.use_ml else "Physics Mode"
        ml_status = QLabel(ml_status_text)
        ml_status.setStyleSheet("""
            font-size: 9pt; 
            padding: 8px; 
            background-color: #d4edda;
            border-radius: 4px;
            color: #2d5016;
            font-weight: 600;
        """ if self.use_ml else """
            font-size: 9pt; 
            padding: 8px; 
            background-color: #e8dcc5;
            border-radius: 4px;
            color: #1e3a5f;
            font-weight: 600;
        """)
        ml_layout.addWidget(ml_status)
        ml_group.setLayout(ml_layout)
        middle_panel.addWidget(ml_group)
        
        # Right panel - Camera feed (DISABLED)
        # Uncomment the section below to re-enable the FPV camera feed
        """
        right_panel = QVBoxLayout()
        right_panel.setSpacing(8)
        
        # Camera header
        camera_header = QHBoxLayout()
        camera_title = QLabel("FPV Camera Feed")
        camera_title.setFont(QFont("Arial", 12, QFont.Bold))
        camera_title.setStyleSheet(
            color: #1e3a5f; 
            padding: 8px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #f5f1e8, stop:1 #ffffff);
            border-radius: 6px;
            border-left: 5px solid #722f37;
        )
        camera_header.addWidget(camera_title)
        right_panel.addLayout(camera_header)
        
        # Camera container with modern styling
        camera_container = QFrame()
        camera_container.setObjectName("cameraContainer")
        camera_container.setStyleSheet(
            #cameraContainer {
                background: #1a1a1a;
                border-radius: 8px;
                border: 2px solid #333333;
            }
        )
        camera_layout = QVBoxLayout(camera_container)
        camera_layout.setContentsMargins(4, 4, 4, 4)
        
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setScaledContents(True)
        self.camera_label.setStyleSheet(
            border: none;
            border-radius: 4px;
            background-color: #000000;
        )
        camera_layout.addWidget(self.camera_label)
        right_panel.addWidget(camera_container)
        """
        
        # Add panels to main layout with better proportions (camera disabled)
        main_layout.addLayout(left_panel, 5)
        main_layout.addLayout(middle_panel, 3)
    
    def apply_stylesheet(self):
        """Apply elegant, classic stylesheet to the application"""
        stylesheet = """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #faf8f3, stop:1 #f0ebe0);
            }
            
            QGroupBox {
                border: 2px solid #c8b896;
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #fdfbf7);
                font-weight: 600;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #1e3a5f;
                background: transparent;
            }
            
            /* Primary action buttons */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c5282, stop:1 #1e3a5f);
                color: white;
                border: 1px solid #1a2f4a;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 9pt;
                font-family: "Arial", "Helvetica", sans-serif;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d6399, stop:1 #2c5282);
                border: 1px solid #d4af37;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a2f4a, stop:1 #0f1f33);
                padding: 10px 17px 8px 19px;
            }
            
            /* Play button - forest green accent */
            QPushButton#playButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3d7218, stop:1 #2d5016);
            }
            
            QPushButton#playButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4d8a20, stop:1 #3d7218);
                border: 1px solid #d4af37;
            }
            
            /* Reset button - amber/gold accent */
            QPushButton#resetButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d4af37, stop:1 #b8860b);
            }
            
            QPushButton#resetButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e5c158, stop:1 #d4af37);
                border: 1px solid #8b6914;
            }
            
            /* Random trajectory button - burgundy accent */
            QPushButton#newTrajButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b3a3a, stop:1 #722f37);
            }
            
            QPushButton#newTrajButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9f4a4a, stop:1 #8b3a3a);
                border: 1px solid #d4af37;
            }
            
            /* Generate button - bronze accent */
            QPushButton#generateButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b6914, stop:1 #6b5410);
            }
            
            QPushButton#generateButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a07c18, stop:1 #8b6914);
                border: 1px solid #d4af37;
            }
            
            /* Apply button - steel blue accent */
            QPushButton#applyButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4682b4, stop:1 #36648b);
            }
            
            QPushButton#applyButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a9bd5, stop:1 #4682b4);
                border: 1px solid #d4af37;
            }
            
            QPushButton#applyButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a8a8a8, stop:1 #888888);
                color: #d0d0d0;
                border: 1px solid #707070;
            }
            
            /* Remove button - dark red accent */
            QPushButton#removeButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a52a2a, stop:1 #8b1a1a);
            }
            
            QPushButton#removeButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c13a3a, stop:1 #a52a2a);
                border: 1px solid #d4af37;
            }
            
            /* Clear button - slate grey accent */
            QPushButton#clearButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6b7280, stop:1 #4b5563);
            }
            
            QPushButton#clearButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7b8290, stop:1 #6b7280);
                border: 1px solid #d4af37;
            }
            
            /* Slider styling */
            QSlider::groove:horizontal {
                border: 1px solid #c8b896;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5f1e8, stop:1 #e8dcc5);
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d4af37, stop:1 #b8860b);
                border: 2px solid #8b6914;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e5c158, stop:1 #d4af37);
                border: 2px solid #6b5410;
            }
            
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d4af37, stop:1 #b8860b);
                border-radius: 4px;
            }
            
            /* Checkbox styling */
            QCheckBox {
                spacing: 8px;
                color: #2c3e50;
                font-weight: 500;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #8b6914;
                background: white;
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #d4af37;
                background: #fdfbf7;
            }
            
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d4af37, stop:1 #b8860b);
                border: 2px solid #8b6914;
            }
            
            QCheckBox::indicator:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e5c158, stop:1 #d4af37);
            }
            
            /* List widget styling */
            QListWidget {
                border: 2px solid #c8b896;
                border-radius: 6px;
                background: white;
                padding: 4px;
                font-size: 9pt;
                font-family: "Arial", "Helvetica", sans-serif;
            }
            
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 4px;
                margin: 2px;
                color: #2c3e50;
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c5282, stop:1 #1e3a5f);
                color: white;
                font-weight: 600;
            }
            
            QListWidget::item:hover {
                background: #f5f1e8;
            }
            
            /* Label styling */
            QLabel {
                color: #2c3e50;
            }
            
            /* Status bar styling */
            QStatusBar {
                background: #ffffff;
                color: #4a4a4a;
                border-top: 2px solid #c8b896;
                font-size: 9pt;
                padding: 4px;
            }
        """
        self.setStyleSheet(stylesheet)
    
    def setup_3d_scene(self):
        """Setup 3D visualization scene"""
        # Grid with warm neutral tint
        grid = gl.GLGridItem()
        grid.scale(2, 2, 1)
        grid.setColor((140, 130, 115, 100))
        self.plot_widget.addItem(grid)
        
        # Trajectory line with elegant golden appearance
        self.trajectory_line = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.83, 0.69, 0.22, 0.9),  # Golden
            width=3.5,
            antialias=True
        )
        self.plot_widget.addItem(self.trajectory_line)
        
        # Drone marker (elegant silver/platinum)
        self.drone_marker = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 5]]),
            color=(0.9, 0.9, 0.95, 1.0),
            size=18,
            pxMode=True
        )
        self.plot_widget.addItem(self.drone_marker)
        
        # Waypoint markers (rich amber/gold)
        self.waypoint_markers = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.85, 0.65, 0.13, 1.0),  # Amber gold
            size=20,
            pxMode=True
        )
        self.plot_widget.addItem(self.waypoint_markers)
        
        # User waypoint markers (bronze/copper)
        self.user_waypoint_markers = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.72, 0.45, 0.20, 1.0),  # Bronze
            size=22,
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
            self.statusBar().showMessage("Dynamic mode enabled - You can now modify waypoints during flight!", 3000)
        else:
            self.apply_changes_btn.setEnabled(False)
            self.statusBar().showMessage("Dynamic mode disabled", 2000)
    
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
            f"Trajectory updated with {len(self.user_waypoints)} waypoints from current position!", 
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
        
        self.statusBar().showMessage(f"Generated random trajectory with {num_waypoints} waypoints", 2000)
    
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
            self.statusBar().showMessage("Simulation playing", 2000)
        else:
            self.play_btn.setText("Play")
            self.timer.stop()
            self.statusBar().showMessage("Simulation paused", 2000)
    
    def reset_simulation(self):
        """Reset simulation to start"""
        self.current_step = 0
        self.is_playing = False
        self.play_btn.setText("Play")
        self.timer.stop()
        self.update_visualization()
        self.statusBar().showMessage("Simulation reset to start", 2000)
    
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
            self.statusBar().showMessage("Simulation complete!", 3000)
        
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
        
        # Update camera view (DISABLED)
        # Uncomment the section below to re-enable camera rendering
        """
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
        """


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    window = DroneSimulationWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
