"""
PyQt5-based 3D simulation with camera feed visualization
"""
import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, QGroupBox,
                             QGridLayout, QLineEdit, QMessageBox, QListWidget, 
                             QListWidgetItem, QSplitter, QFrame, QCheckBox, QStackedLayout)
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
        self.user_waypoints = []  # List of dicts: [{'position': [x,y,z], 'speed': float}, ...]
        self.click_mode_enabled = False
        self.click_height = 10.0  # Default height for clicked waypoints
        self.click_speed = 10.0  # Default speed for clicked waypoints (m/s)
        self.dynamic_mode_enabled = False  # Allow waypoint changes during flight
        self.visited_waypoints = set()  # Track visited waypoints
        self.auto_play_enabled = True  # Auto-play when waypoints are added
        
        # Visual options - all disabled by default
        self.show_trail = False
        self.show_velocity = False
        self.show_connections = False
        self.show_target_line = False
        self.follow_drone_enabled = False
        self.trail_length = 20  # Number of points to show in trail
        
        # Theme settings
        self.current_theme = 'white'  # 'white' or 'black'
        
        # Setup UI
        self.setup_ui()
        self.apply_stylesheet()
        
        # Add status bar
        self.statusBar().showMessage("Ready to simulate drone trajectories", 3000)
        
        # Timer for animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_simulation)
        
        # Start with empty scene (no initial trajectory)
        # User can add waypoints manually or generate random trajectory
        
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
        view_title.setObjectName("viewTitle")
        view_title.setStyleSheet("")  # Will be styled by theme
        view_header.addWidget(view_title)
        left_panel.addLayout(view_header)
        
        # 3D plot container with shadow effect
        plot_container = QFrame()
        plot_container.setObjectName("plot3dContainer")
        plot_container.setStyleSheet("""
            #plot3dContainer {
                background: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """)
        plot_layout = QVBoxLayout(plot_container)
        plot_layout.setContentsMargins(2, 2, 2, 2)
        plot_layout.setSpacing(0)
        
        # Create a stacked widget to overlay legend on 3D view
        from PyQt5.QtWidgets import QStackedLayout
        view_stack = QWidget()
        stack_layout = QStackedLayout(view_stack)
        stack_layout.setStackingMode(QStackedLayout.StackAll)
        
        self.plot_widget = gl.GLViewWidget()
        self.plot_widget.setMinimumSize(900, 580)
        self.plot_widget.setCameraPosition(distance=100)
        self.plot_widget.setBackgroundColor('#ffffff')
        self.plot_widget.setObjectName("plot3d")
        stack_layout.addWidget(self.plot_widget)
        
        # Add legend overlay
        legend_widget = QWidget()
        legend_widget.setAttribute(Qt.WA_TransparentForMouseEvents)
        legend_layout = QVBoxLayout(legend_widget)
        legend_layout.setContentsMargins(10, 10, 10, 10)
        legend_layout.setSpacing(0)
        
        # Legend box
        legend_box = QLabel()
        legend_box.setObjectName("legendBox")
        legend_box.setStyleSheet("")  # Will be styled by theme
        legend_text = """<b>Legend:</b><br>
<span style='color: #3399db;'>●</span> <b>Drone</b> (Blue)<br>
<span style='color: #26a69a;'>●</span> <b>Trajectory WP</b> (Teal)<br>
<span style='color: #ab47ba;'>●</span> <b>User WP</b> (Purple)<br>
<span style='color: #4caf50;'>●</span> <b>Visited</b> (Green)<br>
<span style='color: #ffc107;'>●</span> <b>Target</b> (Gold)<br>
<span style='color: #ff7700;'>━</span> <b>Trail</b> (Orange)<br>
<span style='color: #4caf50;'>→</span> <b>Velocity</b> (Green)<br>
<br><b>Controls:</b><br>
• Left Mouse: Rotate<br>
• Right Mouse: Pan<br>
• Scroll: Zoom"""
        legend_box.setText(legend_text)
        legend_box.setWordWrap(True)
        legend_box.setMaximumWidth(250)
        legend_layout.addWidget(legend_box, 0, Qt.AlignTop | Qt.AlignLeft)
        
        stack_layout.addWidget(legend_widget)
        
        plot_layout.addWidget(view_stack)
        left_panel.addWidget(plot_container)
        
        # Initialize 3D scene
        self.setup_3d_scene()
        
        # Playback controls group
        control_group = QGroupBox("Simulation Controls")
        control_group.setFont(QFont("Arial", 10, QFont.Bold))
        control_layout = QGridLayout()
        control_layout.setSpacing(8)
        control_layout.setContentsMargins(10, 12, 10, 10)
        
        self.play_btn = QPushButton("▶ Play")
        self.play_btn.clicked.connect(self.toggle_play)
        self.play_btn.setMinimumHeight(38)
        self.play_btn.setObjectName("playButton")
        control_layout.addWidget(self.play_btn, 0, 0)
        
        self.reset_btn = QPushButton("⟲ Reset")
        self.reset_btn.clicked.connect(self.reset_simulation)
        self.reset_btn.setMinimumHeight(38)
        self.reset_btn.setObjectName("resetButton")
        control_layout.addWidget(self.reset_btn, 0, 1)
        
        self.new_traj_btn = QPushButton("🎲 Random")
        self.new_traj_btn.clicked.connect(self.generate_new_trajectory)
        self.new_traj_btn.setMinimumHeight(38)
        self.new_traj_btn.setObjectName("newTrajButton")
        control_layout.addWidget(self.new_traj_btn, 0, 2)
        
        speed_label = QLabel("Playback Speed:")
        speed_label.setObjectName("controlLabel")
        control_layout.addWidget(speed_label, 1, 0)
        
        self.playback_speed_slider = QSlider(Qt.Horizontal)
        self.playback_speed_slider.setMinimum(1)
        self.playback_speed_slider.setMaximum(50)
        self.playback_speed_slider.setValue(10)
        self.playback_speed_slider.valueChanged.connect(self.update_speed)
        control_layout.addWidget(self.playback_speed_slider, 1, 1)
        
        self.playback_speed_label = QLabel("1.0x")
        self.playback_speed_label.setObjectName("valueLabel")
        control_layout.addWidget(self.playback_speed_label, 1, 2)
        
        control_group.setLayout(control_layout)
        left_panel.addWidget(control_group)
        
        # Camera controls group
        camera_group = QGroupBox("Camera Controls")
        camera_group.setFont(QFont("Arial", 10, QFont.Bold))
        camera_layout = QGridLayout()
        camera_layout.setSpacing(6)
        camera_layout.setContentsMargins(10, 12, 10, 10)
        
        self.view_top_btn = QPushButton("⬆ Top")
        self.view_top_btn.clicked.connect(lambda: self.set_camera_view('top'))
        self.view_top_btn.setMinimumHeight(32)
        camera_layout.addWidget(self.view_top_btn, 0, 0)
        
        self.view_side_btn = QPushButton("↔ Side")
        self.view_side_btn.clicked.connect(lambda: self.set_camera_view('side'))
        self.view_side_btn.setMinimumHeight(32)
        camera_layout.addWidget(self.view_side_btn, 0, 1)
        
        self.view_front_btn = QPushButton("⬌ Front")
        self.view_front_btn.clicked.connect(lambda: self.set_camera_view('front'))
        self.view_front_btn.setMinimumHeight(32)
        camera_layout.addWidget(self.view_front_btn, 0, 2)
        
        self.view_iso_btn = QPushButton("🔲 Isometric")
        self.view_iso_btn.clicked.connect(lambda: self.set_camera_view('iso'))
        self.view_iso_btn.setMinimumHeight(32)
        camera_layout.addWidget(self.view_iso_btn, 1, 0)
        
        self.follow_drone_checkbox = QCheckBox("Follow Drone")
        self.follow_drone_checkbox.setFont(QFont("Arial", 9))
        self.follow_drone_checkbox.stateChanged.connect(self.toggle_follow_drone)
        camera_layout.addWidget(self.follow_drone_checkbox, 1, 1, 1, 2)
        
        camera_group.setLayout(camera_layout)
        left_panel.addWidget(camera_group)
        
        # Visual options group
        visual_group = QGroupBox("Visual Options")
        visual_group.setFont(QFont("Arial", 10, QFont.Bold))
        visual_layout = QVBoxLayout()
        visual_layout.setSpacing(6)
        visual_layout.setContentsMargins(10, 12, 10, 10)
        
        self.show_trail_checkbox = QCheckBox("Show Trail Effect")
        self.show_trail_checkbox.setFont(QFont("Arial", 9))
        self.show_trail_checkbox.setChecked(False)
        self.show_trail_checkbox.stateChanged.connect(self.toggle_trail)
        visual_layout.addWidget(self.show_trail_checkbox)
        
        self.show_velocity_checkbox = QCheckBox("Show Velocity Vector")
        self.show_velocity_checkbox.setFont(QFont("Arial", 9))
        self.show_velocity_checkbox.setChecked(False)
        self.show_velocity_checkbox.stateChanged.connect(self.toggle_velocity_vector)
        visual_layout.addWidget(self.show_velocity_checkbox)
        
        self.show_connections_checkbox = QCheckBox("Show Waypoint Connections")
        self.show_connections_checkbox.setFont(QFont("Arial", 9))
        self.show_connections_checkbox.setChecked(False)
        self.show_connections_checkbox.stateChanged.connect(self.toggle_connections)
        visual_layout.addWidget(self.show_connections_checkbox)
        
        self.show_target_line_checkbox = QCheckBox("Show Target Line")
        self.show_target_line_checkbox.setFont(QFont("Arial", 9))
        self.show_target_line_checkbox.setChecked(False)
        self.show_target_line_checkbox.stateChanged.connect(self.toggle_target_line)
        visual_layout.addWidget(self.show_target_line_checkbox)
        
        visual_group.setLayout(visual_layout)
        left_panel.addWidget(visual_group)
        
        # Theme selector group
        theme_group = QGroupBox("Theme")
        theme_group.setFont(QFont("Arial", 10, QFont.Bold))
        theme_layout = QHBoxLayout()
        theme_layout.setSpacing(6)
        theme_layout.setContentsMargins(10, 12, 10, 10)
        
        self.white_theme_btn = QPushButton("☀ White")
        self.white_theme_btn.clicked.connect(lambda: self.switch_theme('white'))
        self.white_theme_btn.setMinimumHeight(34)
        self.white_theme_btn.setObjectName("themeButton")
        theme_layout.addWidget(self.white_theme_btn)
        
        self.black_theme_btn = QPushButton("🌙 Black")
        self.black_theme_btn.clicked.connect(lambda: self.switch_theme('black'))
        self.black_theme_btn.setMinimumHeight(34)
        self.black_theme_btn.setObjectName("themeButton")
        theme_layout.addWidget(self.black_theme_btn)
        
        theme_group.setLayout(theme_layout)
        left_panel.addWidget(theme_group)
        
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
        height_lbl.setObjectName("controlLabel")
        height_layout.addWidget(height_lbl)
        
        height_control = QHBoxLayout()
        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setMinimum(5)
        self.height_slider.setMaximum(30)
        self.height_slider.setValue(10)
        self.height_slider.valueChanged.connect(self.update_click_height)
        height_control.addWidget(self.height_slider)
        self.height_label = QLabel("10m")
        self.height_label.setObjectName("valueLabel")
        height_control.addWidget(self.height_label)
        height_layout.addLayout(height_control)
        waypoint_layout.addLayout(height_layout)
        
        # Speed control for clicked waypoints
        speed_layout = QVBoxLayout()
        speed_layout.setSpacing(4)
        speed_lbl = QLabel("Waypoint Speed:")
        speed_lbl.setObjectName("controlLabel")
        speed_layout.addWidget(speed_lbl)
        
        speed_control = QHBoxLayout()
        self.waypoint_speed_slider = QSlider(Qt.Horizontal)
        self.waypoint_speed_slider.setMinimum(1)
        self.waypoint_speed_slider.setMaximum(15)
        self.waypoint_speed_slider.setValue(10)
        self.waypoint_speed_slider.valueChanged.connect(self.update_click_speed)
        speed_control.addWidget(self.waypoint_speed_slider)
        self.waypoint_speed_label = QLabel("10 m/s")
        self.waypoint_speed_label.setObjectName("valueLabel")
        speed_control.addWidget(self.waypoint_speed_label)
        speed_layout.addLayout(speed_control)
        waypoint_layout.addLayout(speed_layout)
        
        # Waypoint list
        list_label = QLabel("Active Waypoints:")
        list_label.setObjectName("controlLabel")
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
        
        # Auto-play mode toggle
        self.auto_play_checkbox = QCheckBox("Auto-Play on Generate")
        self.auto_play_checkbox.setFont(QFont("Arial", 9))
        self.auto_play_checkbox.setChecked(True)
        self.auto_play_checkbox.setStyleSheet("margin-top: 4px;")
        self.auto_play_checkbox.stateChanged.connect(self.toggle_auto_play)
        gen_btn_layout.addWidget(self.auto_play_checkbox)
        
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
            ("Target Speed", "target_speed"),
            ("Time", "time"),
            ("Progress", "progress")
        ]
        
        for i, (label, key) in enumerate(info_items):
            label_widget = QLabel(f"{label}:")
            label_widget.setObjectName("controlLabel")
            info_layout.addWidget(label_widget, i, 0)
            value_label = QLabel("N/A")
            value_label.setObjectName("valueLabel")
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
        ml_status.setObjectName("mlStatusActive" if self.use_ml else "mlStatusPhysics")
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
    
    def switch_theme(self, theme):
        """Switch between white and black themes"""
        self.current_theme = theme
        self.apply_stylesheet()
        
        # Update 3D plot background
        if theme == 'white':
            self.plot_widget.setBackgroundColor('#ffffff')
            self.statusBar().showMessage("Switched to White theme", 2000)
        else:
            self.plot_widget.setBackgroundColor('#1a1a1a')
            self.statusBar().showMessage("Switched to Black theme", 2000)
        
        # Apply theme colors to all 3D scene elements
        self.apply_theme_to_3d_scene()
        
        # Update waypoint labels with appropriate colors
        self.update_waypoint_labels()
    
    def apply_theme_to_3d_scene(self):
        """Apply theme-specific colors to all 3D scene elements"""
        if self.current_theme == 'white':
            # White theme colors - modern and vibrant on white background
            
            # Grid colors
            self.main_grid.setColor((180, 180, 180, 100))  # Light grey
            self.fine_grid.setColor((220, 220, 220, 40))   # Very light grey
            
            # Trajectory line - modern blue
            self.trajectory_line.setData(
                pos=self.trajectory_line.pos,
                color=(0.20, 0.60, 0.86, 0.95)
            )
            
            # Trail line - vibrant orange
            if hasattr(self, 'trail_line'):
                self.trail_line.setData(
                    pos=self.trail_line.pos,
                    color=(1.0, 0.44, 0.0, 0.85)  # Brighter orange for visibility
                )
            
            # Waypoint connections - medium grey
            if hasattr(self, 'waypoint_connections'):
                self.waypoint_connections.setData(
                    pos=self.waypoint_connections.pos,
                    color=(0.4, 0.4, 0.4, 0.5)  # Darker grey for better visibility on white
                )
            
            # Target line - golden yellow
            if hasattr(self, 'target_line'):
                self.target_line.setData(
                    pos=self.target_line.pos,
                    color=(1.0, 0.76, 0.0, 0.7)  # Bright gold
                )
            
            # Velocity vector - vibrant green
            if hasattr(self, 'velocity_vector'):
                self.velocity_vector.setData(
                    pos=self.velocity_vector.pos,
                    color=(0.3, 0.75, 0.3, 0.95)  # Brighter green
                )
            
            # Drone body - modern blue (already set in create_drone_model, but ensure consistency)
            if hasattr(self, 'drone_body'):
                self.drone_body.setColor((0.20, 0.60, 0.86, 1.0))
            
        else:
            # Black theme colors - adjusted for dark background visibility
            
            # Grid colors - lighter for dark background
            self.main_grid.setColor((100, 100, 100, 100))  # Medium grey
            self.fine_grid.setColor((80, 80, 80, 50))      # Dark grey
            
            # Trajectory line - brighter blue for dark background
            self.trajectory_line.setData(
                pos=self.trajectory_line.pos,
                color=(0.35, 0.70, 0.95, 0.95)  # Lighter blue
            )
            
            # Trail line - brighter orange
            if hasattr(self, 'trail_line'):
                self.trail_line.setData(
                    pos=self.trail_line.pos,
                    color=(1.0, 0.55, 0.15, 0.85)  # Bright orange
                )
            
            # Waypoint connections - lighter grey for dark background
            if hasattr(self, 'waypoint_connections'):
                self.waypoint_connections.setData(
                    pos=self.waypoint_connections.pos,
                    color=(0.6, 0.6, 0.6, 0.5)  # Light grey
                )
            
            # Target line - bright golden yellow
            if hasattr(self, 'target_line'):
                self.target_line.setData(
                    pos=self.target_line.pos,
                    color=(1.0, 0.85, 0.2, 0.75)  # Brighter gold
                )
            
            # Velocity vector - bright green
            if hasattr(self, 'velocity_vector'):
                self.velocity_vector.setData(
                    pos=self.velocity_vector.pos,
                    color=(0.4, 0.9, 0.4, 0.95)  # Brighter green
                )
            
            # Drone body - brighter blue for dark background
            if hasattr(self, 'drone_body'):
                self.drone_body.setColor((0.35, 0.70, 0.95, 1.0))
    
    def apply_stylesheet(self):
        """Apply theme-appropriate stylesheet to the application"""
        if self.current_theme == 'white':
            stylesheet = self.get_white_theme_stylesheet()
        else:
            stylesheet = self.get_black_theme_stylesheet()
        
        self.setStyleSheet(stylesheet)
    
    def get_white_theme_stylesheet(self):
        """Get white theme stylesheet"""
        return """
            QMainWindow {
                background: #f5f5f5;
            }
            
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px;
                background: white;
                font-weight: 600;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #2c3e50;
                background: transparent;
            }
            
            /* Primary action buttons */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a9fd4, stop:1 #3498db);
                color: white;
                border: 1px solid #2980b9;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 9pt;
                font-family: "Arial", "Helvetica", sans-serif;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6bb1e0, stop:1 #5a9fd4);
                border: 1px solid #2980b9;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #2471a3);
                padding: 10px 17px 8px 19px;
            }
            
            /* Play button - green accent */
            QPushButton#playButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66bb6a, stop:1 #4caf50);
            }
            
            QPushButton#playButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7bc67e, stop:1 #66bb6a);
                border: 1px solid #43a047;
            }
            
            /* Reset button - orange accent */
            QPushButton#resetButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffa726, stop:1 #ff9800);
            }
            
            QPushButton#resetButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffb74d, stop:1 #ffa726);
                border: 1px solid #f57c00;
            }
            
            /* Random trajectory button - purple accent */
            QPushButton#newTrajButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ab47bc, stop:1 #9c27b0);
            }
            
            QPushButton#newTrajButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ba68c8, stop:1 #ab47bc);
                border: 1px solid #8e24aa;
            }
            
            /* Generate button - teal accent */
            QPushButton#generateButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #26a69a, stop:1 #009688);
            }
            
            QPushButton#generateButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4db6ac, stop:1 #26a69a);
                border: 1px solid #00897b;
            }
            
            /* Apply button - indigo accent */
            QPushButton#applyButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5c6bc0, stop:1 #3f51b5);
            }
            
            QPushButton#applyButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7986cb, stop:1 #5c6bc0);
                border: 1px solid #3949ab;
            }
            
            QPushButton#applyButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #bdbdbd, stop:1 #9e9e9e);
                color: #e0e0e0;
                border: 1px solid #757575;
            }
            
            /* Remove button - red accent */
            QPushButton#removeButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef5350, stop:1 #f44336);
            }
            
            QPushButton#removeButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e57373, stop:1 #ef5350);
                border: 1px solid #e53935;
            }
            
            /* Clear button - grey accent */
            QPushButton#clearButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #78909c, stop:1 #607d8b);
            }
            
            QPushButton#clearButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #90a4ae, stop:1 #78909c);
                border: 1px solid #546e7a;
            }
            
            /* Slider styling */
            QSlider::groove:horizontal {
                border: 1px solid #e0e0e0;
                height: 8px;
                background: #f5f5f5;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a9fd4, stop:1 #3498db);
                border: 2px solid #2980b9;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6bb1e0, stop:1 #5a9fd4);
                border: 2px solid #2471a3;
            }
            
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a9fd4, stop:1 #3498db);
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
                border: 2px solid #bdbdbd;
                background: white;
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #3498db;
                background: #f5f5f5;
            }
            
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a9fd4, stop:1 #3498db);
                border: 2px solid #2980b9;
            }
            
            QCheckBox::indicator:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6bb1e0, stop:1 #5a9fd4);
            }
            
            /* List widget styling */
            QListWidget {
                border: 1px solid #e0e0e0;
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
                    stop:0 #5a9fd4, stop:1 #3498db);
                color: white;
                font-weight: 600;
            }
            
            QListWidget::item:hover {
                background: #f5f5f5;
            }
            
            /* Label styling */
            QLabel {
                color: #2c3e50;
            }
            
            /* Status bar styling */
            QStatusBar {
                background: #ffffff;
                color: #555555;
                border-top: 1px solid #e0e0e0;
                font-size: 9pt;
                padding: 4px;
            }
            
            /* View title styling */
            #viewTitle {
                color: #2c3e50; 
                padding: 8px;
                margin-left: 2px;
                background: white;
                border-radius: 6px;
                border-left: 4px solid #3498db;
            }
            
            /* Legend box styling */
            #legendBox {
                background-color: rgba(255, 255, 255, 230);
                border: 2px solid rgba(52, 152, 219, 180);
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                color: #2c3e50;
            }
            
            /* Control labels */
            #controlLabel {
                font-weight: 600;
                font-size: 9pt;
                color: #555555;
            }
            
            /* Value labels */
            #valueLabel {
                font-size: 9pt;
                color: #3498db;
                font-weight: 600;
            }
            
            /* ML Status labels */
            #mlStatusActive {
                font-size: 9pt;
                padding: 8px;
                background-color: #e8f5e9;
                border-radius: 4px;
                color: #2e7d32;
                font-weight: 600;
            }
            
            #mlStatusPhysics {
                font-size: 9pt;
                padding: 8px;
                background-color: #e3f2fd;
                border-radius: 4px;
                color: #1976d2;
                font-weight: 600;
            }
        """
    
    def get_black_theme_stylesheet(self):
        """Get black theme stylesheet"""
        return """
            QMainWindow {
                background: #1a1a1a;
            }
            
            QGroupBox {
                border: 1px solid #404040;
                border-radius: 8px;
                margin-top: 12px;
                padding: 12px;
                background: #2a2a2a;
                font-weight: 600;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px;
                color: #e0e0e0;
                background: transparent;
            }
            
            /* Primary action buttons */
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a7ba7, stop:1 #2c5f8f);
                color: white;
                border: 1px solid #1f4a73;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 9pt;
                font-family: "Arial", "Helvetica", sans-serif;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a8bb7, stop:1 #3c6f9f);
                border: 1px solid #2c5f8f;
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1f4a73, stop:1 #153a63);
                padding: 10px 17px 8px 19px;
            }
            
            /* Play button - green accent */
            QPushButton#playButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a8f4a, stop:1 #357a38);
            }
            
            QPushButton#playButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a9f5a, stop:1 #458a48);
                border: 1px solid #2d6a30;
            }
            
            /* Reset button - orange accent */
            QPushButton#resetButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cc7a1a, stop:1 #b36200);
            }
            
            QPushButton#resetButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc8a2a, stop:1 #c37210);
                border: 1px solid #a35200;
            }
            
            /* Random trajectory button - purple accent */
            QPushButton#newTrajButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b3a9b, stop:1 #732283);
            }
            
            QPushButton#newTrajButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #9b4aab, stop:1 #833293);
                border: 1px solid #631a73;
            }
            
            /* Generate button - teal accent */
            QPushButton#generateButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a8679, stop:1 #006e61);
            }
            
            QPushButton#generateButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a9689, stop:1 #107e71);
                border: 1px solid #005e51;
            }
            
            /* Apply button - indigo accent */
            QPushButton#applyButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a5ba0, stop:1 #2f3b85);
            }
            
            QPushButton#applyButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6bb0, stop:1 #3f4b95);
                border: 1px solid #1f2b75;
            }
            
            QPushButton#applyButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a, stop:1 #3a3a3a);
                color: #7a7a7a;
                border: 1px solid #2a2a2a;
            }
            
            /* Remove button - red accent */
            QPushButton#removeButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #bf3530, stop:1 #a42a26);
            }
            
            QPushButton#removeButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cf4540, stop:1 #b43a36);
                border: 1px solid #941f1e;
            }
            
            /* Clear button - grey accent */
            QPushButton#clearButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a6a7c, stop:1 #404d5b);
            }
            
            QPushButton#clearButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6a7a8c, stop:1 #505d6b);
                border: 1px solid #303d4b;
            }
            
            /* Slider styling */
            QSlider::groove:horizontal {
                border: 1px solid #404040;
                height: 8px;
                background: #2a2a2a;
                border-radius: 4px;
            }
            
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a7ba7, stop:1 #2c5f8f);
                border: 2px solid #1f4a73;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a8bb7, stop:1 #3c6f9f);
                border: 2px solid #2c5f8f;
            }
            
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a7ba7, stop:1 #2c5f8f);
                border-radius: 4px;
            }
            
            /* Checkbox styling */
            QCheckBox {
                spacing: 8px;
                color: #e0e0e0;
                font-weight: 500;
            }
            
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 4px;
                border: 2px solid #606060;
                background: #2a2a2a;
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #4a7ba7;
                background: #3a3a3a;
            }
            
            QCheckBox::indicator:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a7ba7, stop:1 #2c5f8f);
                border: 2px solid #1f4a73;
            }
            
            QCheckBox::indicator:checked:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a8bb7, stop:1 #3c6f9f);
            }
            
            /* List widget styling */
            QListWidget {
                border: 1px solid #404040;
                border-radius: 6px;
                background: #2a2a2a;
                padding: 4px;
                font-size: 9pt;
                font-family: "Arial", "Helvetica", sans-serif;
            }
            
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 4px;
                margin: 2px;
                color: #e0e0e0;
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a7ba7, stop:1 #2c5f8f);
                color: white;
                font-weight: 600;
            }
            
            QListWidget::item:hover {
                background: #3a3a3a;
            }
            
            /* Label styling */
            QLabel {
                color: #e0e0e0;
            }
            
            /* Status bar styling */
            QStatusBar {
                background: #2a2a2a;
                color: #b0b0b0;
                border-top: 1px solid #404040;
                font-size: 9pt;
                padding: 4px;
            }
            
            /* Frame styling */
            #plot3dContainer {
                background: #1a1a1a;
                border-radius: 8px;
                border: 1px solid #404040;
            }
            
            /* View title styling */
            #viewTitle {
                color: #e0e0e0; 
                padding: 8px;
                margin-left: 2px;
                background: #2a2a2a;
                border-radius: 6px;
                border-left: 4px solid #4a7ba7;
            }
            
            /* Legend box styling */
            #legendBox {
                background-color: rgba(42, 42, 42, 230);
                border: 2px solid rgba(74, 123, 167, 180);
                border-radius: 8px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
                color: #e0e0e0;
            }
            
            /* Control labels */
            #controlLabel {
                font-weight: 600;
                font-size: 9pt;
                color: #b0b0b0;
            }
            
            /* Value labels */
            #valueLabel {
                font-size: 9pt;
                color: #6ba3d4;
                font-weight: 600;
            }
            
            /* ML Status labels */
            #mlStatusActive {
                font-size: 9pt;
                padding: 8px;
                background-color: #1f3f1f;
                border-radius: 4px;
                color: #5faf5f;
                font-weight: 600;
            }
            
            #mlStatusPhysics {
                font-size: 9pt;
                padding: 8px;
                background-color: #1f2f3f;
                border-radius: 4px;
                color: #4a8fd4;
                font-weight: 600;
            }
        """
    
    def setup_3d_scene(self):
        """Setup 3D visualization scene with enhanced graphics"""
        # Main grid (major grid lines) - theme-compliant
        self.main_grid = gl.GLGridItem()
        self.main_grid.scale(5, 5, 1)
        # Will be set by apply_theme_to_3d_scene()
        self.plot_widget.addItem(self.main_grid)
        
        # Fine grid (minor grid lines) - theme-compliant
        self.fine_grid = gl.GLGridItem()
        self.fine_grid.scale(1, 1, 1)
        # Will be set by apply_theme_to_3d_scene()
        self.plot_widget.addItem(self.fine_grid)
        
        # Add coordinate axes
        self.setup_axes()
        
        # Trajectory line with enhanced appearance - theme-compliant
        self.trajectory_line = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.20, 0.60, 0.86, 0.95),  # Will be updated by theme
            width=4.0,
            antialias=True
        )
        self.plot_widget.addItem(self.trajectory_line)
        
        # Trail effect (shows recent path) - theme-compliant
        self.trail_line = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.95, 0.40, 0.20, 0.8),  # Will be updated by theme
            width=6.0,
            antialias=True
        )
        self.plot_widget.addItem(self.trail_line)
        
        # Waypoint connection lines - theme-compliant
        self.waypoint_connections = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.30, 0.30, 0.30, 0.4),  # Will be updated by theme
            width=2.0,
            antialias=True,
            mode='line_strip'
        )
        self.plot_widget.addItem(self.waypoint_connections)
        
        # Current target line (from drone to current waypoint) - theme-compliant
        self.target_line = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0], [0, 0, 0]]),
            color=(1.0, 0.8, 0.0, 0.6),  # Will be updated by theme
            width=2.5,
            antialias=True
        )
        self.plot_widget.addItem(self.target_line)
        
        # Velocity vector - theme-compliant
        self.velocity_vector = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0], [0, 0, 0]]),
            color=(0.2, 0.8, 0.2, 0.9),  # Will be updated by theme
            width=3.0,
            antialias=True
        )
        self.plot_widget.addItem(self.velocity_vector)
        
        # Create 3D drone model with propellers
        self.create_drone_model()
        self.propeller_rotation = 0.0  # Track propeller rotation angle
        
        # Waypoint markers with glow - theme-compliant (teal for generated waypoints)
        self.waypoint_markers_glow = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.15, 0.65, 0.60, 0.25),  # Teal glow - theme-compliant
            size=20,
            pxMode=True
        )
        self.plot_widget.addItem(self.waypoint_markers_glow)
        
        self.waypoint_markers = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.15, 0.65, 0.60, 1.0),  # Teal - theme-compliant
            size=12,
            pxMode=True
        )
        self.plot_widget.addItem(self.waypoint_markers)
        
        # Waypoint text labels - list to store text items
        self.waypoint_text_items = []
        
        # Current target waypoint highlight (animated)
        self.target_waypoint_marker = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(1.0, 0.8, 0.0, 0.9),  # Golden
            size=18,
            pxMode=True
        )
        self.plot_widget.addItem(self.target_waypoint_marker)
        
        # User waypoint markers with glow - theme-compliant (purple for user waypoints)
        self.user_waypoint_markers_glow = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.67, 0.28, 0.73, 0.25),  # Purple glow - theme-compliant
            size=22,
            pxMode=True
        )
        self.plot_widget.addItem(self.user_waypoint_markers_glow)
        
        self.user_waypoint_markers = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.67, 0.28, 0.73, 1.0),  # Purple - theme-compliant
            size=14,
            pxMode=True
        )
        self.plot_widget.addItem(self.user_waypoint_markers)
        
        # Animation timer for pulsing effects
        self.animation_phase = 0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animations)
        self.animation_timer.start(50)  # 20 FPS for animations
        
        # Connect mouse events
        self.plot_widget.mousePressEvent = self.on_3d_click
        
        # Apply initial theme colors to 3D scene
        self.apply_theme_to_3d_scene()
    
    def setup_axes(self):
        """Setup coordinate axes with labels"""
        axis_length = 50
        axis_width = 3.0
        
        # X axis (Red)
        x_axis = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0], [axis_length, 0, 0]]),
            color=(0.9, 0.2, 0.2, 0.7),
            width=axis_width,
            antialias=True
        )
        self.plot_widget.addItem(x_axis)
        
        # Y axis (Green)
        y_axis = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0], [0, axis_length, 0]]),
            color=(0.2, 0.9, 0.2, 0.7),
            width=axis_width,
            antialias=True
        )
        self.plot_widget.addItem(y_axis)
        
        # Z axis (Blue)
        z_axis = gl.GLLinePlotItem(
            pos=np.array([[0, 0, 0], [0, 0, axis_length]]),
            color=(0.2, 0.2, 0.9, 0.7),
            width=axis_width,
            antialias=True
        )
        self.plot_widget.addItem(z_axis)
    
    def create_drone_model(self):
        """Create a 3D drone model with body, arms, and propellers"""
        # Drone body (center sphere) - theme-compliant blue
        md = gl.MeshData.sphere(rows=10, cols=10, radius=0.8)
        self.drone_body = gl.GLMeshItem(
            meshdata=md,
            color=(0.20, 0.60, 0.86, 1.0),  # Modern blue - theme-compliant
            smooth=True,
            shader='shaded',
            glOptions='opaque'
        )
        self.plot_widget.addItem(self.drone_body)
        
        # Drone arms (4 cylinders extending from center)
        self.drone_arms = []
        arm_positions = [
            (1, 0, 0),   # Front
            (-1, 0, 0),  # Back
            (0, 1, 0),   # Right
            (0, -1, 0)   # Left
        ]
        
        for pos in arm_positions:
            # Create arm mesh
            arm_mesh = self.create_cylinder_mesh(length=2.0, radius=0.15)
            arm = gl.GLMeshItem(
                meshdata=arm_mesh,
                color=(0.3, 0.3, 0.3, 1.0),
                smooth=True,
                shader='shaded',
                glOptions='opaque'
            )
            self.drone_arms.append((arm, pos))
            self.plot_widget.addItem(arm)
        
        # Propellers (4 sets of 2 blades each)
        self.propellers = []
        for pos in arm_positions:
            # Two blades per propeller
            blade1 = self.create_propeller_blade()
            blade2 = self.create_propeller_blade()
            
            blade1_item = gl.GLMeshItem(
                meshdata=blade1,
                color=(0.1, 0.1, 0.1, 0.9),
                smooth=True,
                shader='shaded',
                glOptions='translucent'
            )
            blade2_item = gl.GLMeshItem(
                meshdata=blade2,
                color=(0.1, 0.1, 0.1, 0.9),
                smooth=True,
                shader='shaded',
                glOptions='translucent'
            )
            
            self.plot_widget.addItem(blade1_item)
            self.plot_widget.addItem(blade2_item)
            
            # Store blade items with their position
            self.propellers.append({
                'blade1': blade1_item,
                'blade2': blade2_item,
                'position': pos
            })
    
    def create_cylinder_mesh(self, length=2.0, radius=0.15, segments=8):
        """Create a cylinder mesh for drone arms"""
        # Create cylinder vertices
        verts = []
        faces = []
        
        # Create rings
        for i in range(2):  # Two rings (start and end)
            z = (i - 0.5) * length
            for j in range(segments):
                angle = 2 * np.pi * j / segments
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                verts.append([x, y, z])
        
        # Create faces
        for j in range(segments):
            next_j = (j + 1) % segments
            # Two triangles per face
            faces.append([j, next_j, j + segments])
            faces.append([next_j, next_j + segments, j + segments])
        
        # Add caps
        center_start = len(verts)
        verts.append([0, 0, -length/2])
        center_end = len(verts)
        verts.append([0, 0, length/2])
        
        for j in range(segments):
            next_j = (j + 1) % segments
            faces.append([center_start, next_j, j])
            faces.append([center_end, j + segments, next_j + segments])
        
        verts = np.array(verts)
        faces = np.array(faces)
        
        md = gl.MeshData(vertexes=verts, faces=faces)
        return md
    
    def create_propeller_blade(self):
        """Create a single propeller blade mesh"""
        # Simple rectangular blade with slight curve
        verts = np.array([
            # Top surface
            [-1.2, -0.15, 0.05],
            [1.2, -0.15, 0.05],
            [1.2, 0.15, 0.05],
            [-1.2, 0.15, 0.05],
            # Bottom surface
            [-1.2, -0.15, -0.05],
            [1.2, -0.15, -0.05],
            [1.2, 0.15, -0.05],
            [-1.2, 0.15, -0.05],
        ])
        
        faces = np.array([
            # Top
            [0, 1, 2], [0, 2, 3],
            # Bottom
            [4, 6, 5], [4, 7, 6],
            # Sides
            [0, 4, 5], [0, 5, 1],
            [1, 5, 6], [1, 6, 2],
            [2, 6, 7], [2, 7, 3],
            [3, 7, 4], [3, 4, 0],
        ])
        
        md = gl.MeshData(vertexes=verts, faces=faces)
        return md
    
    def update_drone_model_position(self, position, velocity):
        """Update drone model position and orientation"""
        # Update body position
        transform = np.eye(4)
        transform[:3, 3] = position
        self.drone_body.setTransform(transform)
        
        # Calculate orientation from velocity
        if np.linalg.norm(velocity) > 0.1:
            # Yaw angle (rotation around Z axis)
            yaw = np.arctan2(velocity[1], velocity[0])
            
            # Pitch angle (tilt based on horizontal velocity)
            horizontal_speed = np.sqrt(velocity[0]**2 + velocity[1]**2)
            pitch = np.arctan2(velocity[2], horizontal_speed) * 0.3  # Reduced tilt
        else:
            yaw = 0
            pitch = 0
        
        # Update arms
        for arm, arm_pos in self.drone_arms:
            # Rotate arm position based on yaw
            angle = np.arctan2(arm_pos[1], arm_pos[0])
            rotated_angle = angle + yaw
            
            arm_world_x = position[0] + 1.5 * np.cos(rotated_angle)
            arm_world_y = position[1] + 1.5 * np.sin(rotated_angle)
            arm_world_z = position[2]
            
            # Create transformation matrix for arm
            arm_transform = np.eye(4)
            
            # Rotation matrix for arm orientation
            c = np.cos(rotated_angle)
            s = np.sin(rotated_angle)
            arm_transform[0, 0] = c
            arm_transform[0, 1] = -s
            arm_transform[1, 0] = s
            arm_transform[1, 1] = c
            
            # Position
            arm_transform[:3, 3] = [arm_world_x, arm_world_y, arm_world_z]
            
            arm.setTransform(arm_transform)
        
        # Update propellers with rotation
        self.propeller_rotation += 30.0  # Degrees per frame
        if self.propeller_rotation > 360:
            self.propeller_rotation -= 360
        
        for i, prop in enumerate(self.propellers):
            arm_pos = prop['position']
            
            # Calculate propeller world position
            angle = np.arctan2(arm_pos[1], arm_pos[0])
            rotated_angle = angle + yaw
            
            prop_world_x = position[0] + 2.5 * np.cos(rotated_angle)
            prop_world_y = position[1] + 2.5 * np.sin(rotated_angle)
            prop_world_z = position[2]
            
            # Blade 1 rotation
            blade1_transform = np.eye(4)
            rot_angle1 = np.radians(self.propeller_rotation)
            c1 = np.cos(rot_angle1)
            s1 = np.sin(rot_angle1)
            blade1_transform[0, 0] = c1
            blade1_transform[0, 1] = -s1
            blade1_transform[1, 0] = s1
            blade1_transform[1, 1] = c1
            blade1_transform[:3, 3] = [prop_world_x, prop_world_y, prop_world_z]
            prop['blade1'].setTransform(blade1_transform)
            
            # Blade 2 rotation (90 degrees offset)
            blade2_transform = np.eye(4)
            rot_angle2 = np.radians(self.propeller_rotation + 90)
            c2 = np.cos(rot_angle2)
            s2 = np.sin(rot_angle2)
            blade2_transform[0, 0] = c2
            blade2_transform[0, 1] = -s2
            blade2_transform[1, 0] = s2
            blade2_transform[1, 1] = c2
            blade2_transform[:3, 3] = [prop_world_x, prop_world_y, prop_world_z]
            prop['blade2'].setTransform(blade2_transform)
    
    def update_animations(self):
        """Update animated elements like pulsing markers - theme-compliant"""
        self.animation_phase = (self.animation_phase + 0.1) % (2 * np.pi)
        pulse = 0.8 + 0.2 * np.sin(self.animation_phase)
        
        # Pulse the target waypoint marker with theme-compliant colors
        if self.current_trajectory is not None and self.current_step < len(self.current_trajectory['positions']):
            waypoints = self.current_trajectory['waypoints']
            wp_indices = self.current_trajectory['waypoint_indices']
            wp_idx = min(wp_indices[self.current_step], len(waypoints) - 1)
            
            # Theme-compliant gold color for target waypoint
            if self.current_theme == 'white':
                target_color = (1.0, 0.76, 0.0, 0.9)  # Gold
            else:
                target_color = (1.0, 0.85, 0.2, 0.95)  # Brighter gold for dark background
            
            # Update target waypoint size with pulse and color
            self.target_waypoint_marker.setData(
                pos=np.array([waypoints[wp_idx]]),
                size=int(18 * pulse),
                color=target_color
            )
    
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
    
    def update_click_speed(self, value):
        """Update the speed for clicked waypoints"""
        self.click_speed = float(value)
        self.waypoint_speed_label.setText(f"{value} m/s")
    
    def add_waypoint(self, position, speed=None):
        """Add a waypoint to the list"""
        if speed is None:
            speed = self.click_speed
        
        waypoint = {
            'position': position,
            'speed': speed
        }
        self.user_waypoints.append(waypoint)
        
        # Update the list widget
        item_text = f"WP {len(self.user_waypoints)}: ({position[0]:.1f}, {position[1]:.1f}, {position[2]:.1f}) @ {speed:.1f} m/s"
        self.waypoint_list.addItem(item_text)
        
        # Update visualization
        self.update_user_waypoint_markers()
        
        message = f"Added waypoint at ({position[0]:.1f}, {position[1]:.1f}, {position[2]:.1f}) with speed {speed:.1f} m/s"
        
        # If in dynamic mode and trajectory is running, prompt to apply changes
        if self.dynamic_mode_enabled and self.current_trajectory is not None:
            message += " - Click 'Apply Changes' to update trajectory"
        
        self.statusBar().showMessage(message, 3000)
    
    def remove_selected_waypoint(self):
        """Remove the selected waypoint from the list"""
        current_row = self.waypoint_list.currentRow()
        if current_row >= 0:
            self.waypoint_list.takeItem(current_row)
            del self.user_waypoints[current_row]
            
            # Update list numbering
            for i in range(self.waypoint_list.count()):
                wp = self.user_waypoints[i]
                pos = wp['position']
                speed = wp['speed']
                self.waypoint_list.item(i).setText(
                    f"WP {i+1}: ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}) @ {speed:.1f} m/s"
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
        """Update the visual markers for user waypoints - theme-compliant"""
        if self.user_waypoints:
            positions = np.array([wp['position'] for wp in self.user_waypoints])
            
            # Theme-compliant colors for user waypoints (purple)
            if self.current_theme == 'white':
                color = (0.67, 0.28, 0.73, 1.0)      # Purple
                glow_color = (0.67, 0.28, 0.73, 0.25)
            else:
                color = (0.77, 0.38, 0.83, 1.0)      # Brighter purple for dark background
                glow_color = (0.77, 0.38, 0.83, 0.25)
            
            self.user_waypoint_markers.setData(pos=positions, color=color)
            self.user_waypoint_markers_glow.setData(pos=positions, color=glow_color)
        else:
            # Hide markers by placing them off-screen
            self.user_waypoint_markers.setData(pos=np.array([[1000, 1000, 1000]]))
            self.user_waypoint_markers_glow.setData(pos=np.array([[1000, 1000, 1000]]))
    
    def toggle_auto_play(self, state):
        """Toggle auto-play mode"""
        self.auto_play_enabled = (state == Qt.Checked)
        
        if self.auto_play_enabled:
            self.statusBar().showMessage("Auto-play enabled - Trajectory will start automatically", 2000)
        else:
            self.statusBar().showMessage("Auto-play disabled - Click Play to start", 2000)
    
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
        
        # Update waypoints and speeds
        self.current_trajectory['waypoints'] = new_trajectory['waypoints']
        self.current_trajectory['waypoint_speeds'] = new_trajectory['waypoint_speeds']
        
        # Reset visited waypoints since we have a new set of waypoints
        self.visited_waypoints.clear()
        
        # Update visualization
        self.update_3d_scene()
        
        # Resume playing if it was already playing
        if not self.is_playing and self.auto_play_enabled:
            self.toggle_play()
        
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
        
        # Reset visited waypoints for new trajectory
        self.visited_waypoints.clear()
        
        # Update visualization
        self.update_3d_scene()
        self.reset_simulation()
        
        # Auto-play if enabled
        if self.auto_play_enabled and not self.is_playing:
            self.toggle_play()
        
        self.statusBar().showMessage(f"Generated trajectory with {len(self.user_waypoints)} waypoints", 3000)
    
    def generate_new_trajectory(self):
        """Generate a new random trajectory"""
        # Random initial conditions
        initial_pos = np.array([0, 0, 5])
        initial_vel = np.array([0, 0, 0])
        
        # Random waypoints with speeds
        num_waypoints = np.random.randint(3, 6)
        waypoints = []
        for _ in range(num_waypoints):
            pos = np.array([
                np.random.uniform(-30, 30),
                np.random.uniform(-30, 30),
                np.random.uniform(5, 20)
            ])
            speed = np.random.uniform(5, 12)  # Random speed between 5-12 m/s
            waypoints.append({'position': pos, 'speed': speed})
        
        # Generate trajectory
        self.current_trajectory = self.trajectory_generator.generate(
            initial_pos, initial_vel, waypoints
        )
        
        # Reset visited waypoints for new trajectory
        self.visited_waypoints.clear()
        
        # Update visualization
        self.update_3d_scene()
        self.reset_simulation()
        
        # Auto-play if enabled
        if self.auto_play_enabled and not self.is_playing:
            self.toggle_play()
        
        self.statusBar().showMessage(f"Generated random trajectory with {num_waypoints} waypoints", 2000)
    
    def update_waypoint_colors(self):
        """Update waypoint colors based on visited status - theme-compliant"""
        if self.current_trajectory is None:
            return
        
        waypoints = self.current_trajectory['waypoints']
        num_waypoints = len(waypoints)
        
        # Create color array for each waypoint
        colors = np.zeros((num_waypoints, 4))
        colors_glow = np.zeros((num_waypoints, 4))
        
        # Theme-compliant colors
        if self.current_theme == 'white':
            # White theme colors
            visited_color = [0.3, 0.75, 0.3, 1.0]      # Vibrant green for visited
            visited_glow = [0.3, 0.75, 0.3, 0.25]
            unvisited_color = [0.15, 0.65, 0.60, 1.0]  # Teal for unvisited
            unvisited_glow = [0.15, 0.65, 0.60, 0.25]
        else:
            # Black theme colors - brighter for visibility
            visited_color = [0.4, 0.9, 0.4, 1.0]       # Bright green for visited
            visited_glow = [0.4, 0.9, 0.4, 0.25]
            unvisited_color = [0.2, 0.75, 0.70, 1.0]   # Bright teal for unvisited
            unvisited_glow = [0.2, 0.75, 0.70, 0.25]
        
        for i in range(num_waypoints):
            if i in self.visited_waypoints:
                colors[i] = visited_color
                colors_glow[i] = visited_glow
            else:
                colors[i] = unvisited_color
                colors_glow[i] = unvisited_glow
        
        # Update markers with new colors
        self.waypoint_markers.setData(pos=waypoints, color=colors)
        self.waypoint_markers_glow.setData(pos=waypoints, color=colors_glow)
    
    def update_waypoint_labels(self):
        """Update waypoint text labels"""
        # Remove old text items
        for text_item in self.waypoint_text_items:
            self.plot_widget.removeItem(text_item)
        self.waypoint_text_items.clear()
        
        if self.current_trajectory is None:
            return
        
        waypoints = self.current_trajectory['waypoints']
        
        # Create text label for each waypoint
        for i, wp in enumerate(waypoints):
            # Determine color based on visited status and theme
            if i in self.visited_waypoints:
                # Green for visited (brighter for visibility)
                color = (0.0, 1.0, 0.0, 1.0) if self.current_theme == 'white' else (0.2, 1.0, 0.2, 1.0)
            else:
                # High contrast colors for unvisited based on theme
                if self.current_theme == 'white':
                    color = (0.0, 0.0, 0.0, 1.0)  # Black on white background
                else:
                    color = (1.0, 1.0, 1.0, 1.0)  # White on black background
            
            # Create text item with waypoint number - larger and bolder for better visibility
            text = gl.GLTextItem(
                pos=(wp[0], wp[1], wp[2] + 2.5),  # Position slightly higher above waypoint
                text=f"WP{i + 1}",  # Add "WP" prefix for clarity
                color=color,
                font=pg.QtGui.QFont('Arial', 14, pg.QtGui.QFont.Bold)
            )
            self.plot_widget.addItem(text)
            self.waypoint_text_items.append(text)
    
    def update_3d_scene(self):
        """Update 3D scene with current trajectory"""
        if self.current_trajectory is None:
            return
        
        # Update trajectory line
        positions = self.current_trajectory['positions']
        self.trajectory_line.setData(pos=positions)
        
        # Update waypoint markers with colors
        self.update_waypoint_colors()
        
        # Update waypoint text labels
        self.update_waypoint_labels()
        
        # Update waypoint connections
        waypoints = self.current_trajectory['waypoints']
        if len(waypoints) > 1:
            self.waypoint_connections.setData(pos=waypoints)
    
    def toggle_play(self):
        """Toggle play/pause"""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_btn.setText("⏸ Pause")
            self.timer.start(int(100 / self.playback_speed))  # 100ms base
            self.statusBar().showMessage("Simulation playing", 2000)
        else:
            self.play_btn.setText("▶ Play")
            self.timer.stop()
            self.statusBar().showMessage("Simulation paused", 2000)
    
    def set_camera_view(self, view_type):
        """Set predefined camera views"""
        if view_type == 'top':
            self.plot_widget.setCameraPosition(elevation=90, azimuth=0, distance=100)
            self.statusBar().showMessage("Camera: Top View", 2000)
        elif view_type == 'side':
            self.plot_widget.setCameraPosition(elevation=0, azimuth=0, distance=100)
            self.statusBar().showMessage("Camera: Side View", 2000)
        elif view_type == 'front':
            self.plot_widget.setCameraPosition(elevation=0, azimuth=90, distance=100)
            self.statusBar().showMessage("Camera: Front View", 2000)
        elif view_type == 'iso':
            self.plot_widget.setCameraPosition(elevation=30, azimuth=45, distance=100)
            self.statusBar().showMessage("Camera: Isometric View", 2000)
    
    def toggle_follow_drone(self, state):
        """Toggle camera follow mode for drone"""
        self.follow_drone_enabled = (state == Qt.Checked)
        if self.follow_drone_enabled:
            self.statusBar().showMessage("Follow mode enabled - Camera will track drone", 2000)
        else:
            self.statusBar().showMessage("Follow mode disabled", 2000)
    
    def toggle_trail(self, state):
        """Toggle trail effect visibility"""
        self.show_trail = (state == Qt.Checked)
        if not self.show_trail:
            self.trail_line.setData(pos=np.array([[0, 0, 0]]))
    
    def toggle_velocity_vector(self, state):
        """Toggle velocity vector visibility"""
        self.show_velocity = (state == Qt.Checked)
        if not self.show_velocity:
            self.velocity_vector.setData(pos=np.array([[0, 0, 0], [0, 0, 0]]))
    
    def toggle_connections(self, state):
        """Toggle waypoint connections visibility"""
        self.show_connections = (state == Qt.Checked)
        if not self.show_connections:
            self.waypoint_connections.setData(pos=np.array([[0, 0, 0]]))
        else:
            self.update_3d_scene()
    
    def toggle_target_line(self, state):
        """Toggle target line visibility"""
        self.show_target_line = (state == Qt.Checked)
        if not self.show_target_line:
            self.target_line.setData(pos=np.array([[0, 0, 0], [0, 0, 0]]))
    
    def reset_simulation(self):
        """Reset simulation to start"""
        self.current_step = 0
        self.is_playing = False
        self.play_btn.setText("▶ Play")
        self.timer.stop()
        
        # Reset visited waypoints
        self.visited_waypoints.clear()
        
        # Update visualization to reflect reset state
        if self.current_trajectory is not None:
            self.update_waypoint_colors()
            self.update_waypoint_labels()
            self.update_visualization()
        
        self.statusBar().showMessage("Simulation reset to start", 2000)
    
    def update_speed(self, value):
        """Update playback speed"""
        self.playback_speed = value / 10.0
        self.playback_speed_label.setText(f"{self.playback_speed:.1f}x")
        
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
            self.play_btn.setText("▶ Play")
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
        
        # Check if any waypoints have been visited (within threshold distance)
        visit_threshold = 2.0  # meters
        for i, wp in enumerate(waypoints):
            distance_to_wp = np.linalg.norm(wp - pos)
            if distance_to_wp < visit_threshold:
                if i not in self.visited_waypoints:
                    self.visited_waypoints.add(i)
                    # Update colors when a new waypoint is visited
                    self.update_waypoint_colors()
                    self.update_waypoint_labels()
        
        # Update 3D drone model with rotation and position
        self.update_drone_model_position(pos, vel)
        
        # Update trail effect
        if self.show_trail and self.current_step > 0:
            trail_start = max(0, self.current_step - self.trail_length)
            trail_positions = positions[trail_start:self.current_step + 1]
            if len(trail_positions) > 1:
                self.trail_line.setData(pos=trail_positions)
        
        # Update velocity vector
        if self.show_velocity:
            vel_magnitude = np.linalg.norm(vel)
            if vel_magnitude > 0.1:
                # Scale velocity vector for visibility
                vel_scaled = vel * 3.0
                vel_end = pos + vel_scaled
                self.velocity_vector.setData(pos=np.array([pos, vel_end]))
        
        # Update target line (drone to current waypoint)
        if self.show_target_line:
            self.target_line.setData(pos=np.array([pos, current_wp]))
        
        # Camera follow mode
        if self.follow_drone_enabled:
            # Center camera on drone position
            self.plot_widget.opts['center'] = pg.Vector(pos[0], pos[1], pos[2])
        
        # Calculate additional metrics
        distance_to_wp = np.linalg.norm(current_wp - pos)
        speed = np.linalg.norm(vel)
        
        # Get target speed for current waypoint
        waypoint_speeds = self.current_trajectory.get('waypoint_speeds', None)
        if waypoint_speeds is not None and wp_idx < len(waypoint_speeds):
            target_speed = waypoint_speeds[wp_idx]
        else:
            target_speed = 10.0  # Default
        
        # Update info labels
        self.info_labels['position'].setText(
            f"({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})"
        )
        self.info_labels['velocity'].setText(
            f"{speed:.2f} m/s | ({vel[0]:.1f}, {vel[1]:.1f}, {vel[2]:.1f})"
        )
        self.info_labels['acceleration'].setText(
            f"({acc[0]:.2f}, {acc[1]:.2f}, {acc[2]:.2f}) m/s²"
        )
        self.info_labels['waypoint'].setText(
            f"#{wp_idx+1} | Dist: {distance_to_wp:.1f}m"
        )
        self.info_labels['target_speed'].setText(f"{target_speed:.1f} m/s")
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
