"""
PyQt5-based 3D simulation with camera feed visualization
"""
import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, QGroupBox,
                             QGridLayout, QLineEdit, QMessageBox, QListWidget, 
                             QListWidgetItem, QSplitter, QFrame, QCheckBox, QStackedLayout,
                             QMenuBar, QMenu, QAction, QDialog, QDialogButtonBox, QSpinBox,
                             QDoubleSpinBox, QTextEdit, QScrollArea, QFormLayout, QComboBox,
                             QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QFont, QColor, QPalette
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import cv2
from trajectory_generator import TrajectoryGenerator
from ml_model import TrajectoryPredictor
from trajectory_storage import TrajectoryStorage
from trajectory_templates import TrajectoryTemplates
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


class SettingsDialog(QDialog):
    """Settings dialog for configuring application preferences"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Create scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QFormLayout(scroll_widget)
        scroll_layout.setSpacing(12)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        
        # Visual Options Section
        visual_label = QLabel("<b>Visual Options</b>")
        scroll_layout.addRow(visual_label)
        
        self.trail_checkbox = QCheckBox()
        self.trail_checkbox.setChecked(parent.show_trail if parent else False)
        scroll_layout.addRow("Show Trail Effect:", self.trail_checkbox)
        
        self.velocity_checkbox = QCheckBox()
        self.velocity_checkbox.setChecked(parent.show_velocity if parent else False)
        scroll_layout.addRow("Show Velocity Vector:", self.velocity_checkbox)
        
        self.connections_checkbox = QCheckBox()
        self.connections_checkbox.setChecked(parent.show_connections if parent else False)
        scroll_layout.addRow("Show Waypoint Connections:", self.connections_checkbox)
        
        self.target_line_checkbox = QCheckBox()
        self.target_line_checkbox.setChecked(parent.show_target_line if parent else False)
        scroll_layout.addRow("Show Target Line:", self.target_line_checkbox)
        
        self.trail_length_spin = QSpinBox()
        self.trail_length_spin.setRange(5, 100)
        self.trail_length_spin.setValue(parent.trail_length if parent else 20)
        scroll_layout.addRow("Trail Length (points):", self.trail_length_spin)
        
        # Theme Section
        theme_label = QLabel("<b>Theme Settings</b>")
        scroll_layout.addRow(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["White", "Black"])
        current_theme = parent.current_theme if parent else 'white'
        self.theme_combo.setCurrentText(current_theme.capitalize())
        scroll_layout.addRow("Color Theme:", self.theme_combo)
        
        # Camera Section
        camera_label = QLabel("<b>Camera Settings</b>")
        scroll_layout.addRow(camera_label)
        
        self.follow_drone_checkbox = QCheckBox()
        self.follow_drone_checkbox.setChecked(parent.follow_drone_enabled if parent else False)
        scroll_layout.addRow("Follow Drone Mode:", self.follow_drone_checkbox)
        
        # Playback Section
        playback_label = QLabel("<b>Playback Settings</b>")
        scroll_layout.addRow(playback_label)
        
        self.playback_speed_spin = QDoubleSpinBox()
        self.playback_speed_spin.setRange(0.1, 5.0)
        self.playback_speed_spin.setSingleStep(0.1)
        self.playback_speed_spin.setValue(parent.playback_speed if parent else 1.0)
        scroll_layout.addRow("Playback Speed:", self.playback_speed_spin)
        
        self.auto_play_checkbox = QCheckBox()
        self.auto_play_checkbox.setChecked(parent.auto_play_enabled if parent else True)
        scroll_layout.addRow("Auto-Play on Generate:", self.auto_play_checkbox)
        
        # Waypoint Section
        waypoint_label = QLabel("<b>Waypoint Settings</b>")
        scroll_layout.addRow(waypoint_label)
        
        self.click_height_spin = QDoubleSpinBox()
        self.click_height_spin.setRange(1.0, 100.0)
        self.click_height_spin.setValue(parent.click_height if parent else 10.0)
        scroll_layout.addRow("Click Waypoint Height (m):", self.click_height_spin)
        
        self.click_speed_spin = QDoubleSpinBox()
        self.click_speed_spin.setRange(0.1, 50.0)
        self.click_speed_spin.setValue(parent.click_speed if parent else 10.0)
        scroll_layout.addRow("Click Waypoint Speed (m/s):", self.click_speed_spin)
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def apply_settings(self):
        """Apply settings to parent window"""
        if self.parent_window:
            # Visual options
            self.parent_window.show_trail = self.trail_checkbox.isChecked()
            self.parent_window.show_velocity = self.velocity_checkbox.isChecked()
            self.parent_window.show_connections = self.connections_checkbox.isChecked()
            self.parent_window.show_target_line = self.target_line_checkbox.isChecked()
            self.parent_window.trail_length = self.trail_length_spin.value()
            
            # Theme
            new_theme = self.theme_combo.currentText().lower()
            if new_theme != self.parent_window.current_theme:
                self.parent_window.switch_theme(new_theme)
            
            # Camera
            was_following = self.parent_window.follow_drone_enabled
            self.parent_window.follow_drone_enabled = self.follow_drone_checkbox.isChecked()
            self.parent_window.follow_drone_checkbox.setChecked(self.follow_drone_checkbox.isChecked())
            
            # Playback
            self.parent_window.playback_speed = self.playback_speed_spin.value()
            slider_value = int(self.playback_speed_spin.value() * 10)
            self.parent_window.playback_speed_slider.setValue(slider_value)
            
            self.parent_window.auto_play_enabled = self.auto_play_checkbox.isChecked()
            self.parent_window.auto_play_checkbox.setChecked(self.auto_play_checkbox.isChecked())
            
            # Waypoints
            self.parent_window.click_height = self.click_height_spin.value()
            self.parent_window.height_input.setText(str(self.click_height_spin.value()))
            
            self.parent_window.click_speed = self.click_speed_spin.value()
            self.parent_window.waypoint_speed_input.setText(str(self.click_speed_spin.value()))
            
            # Update visualization
            self.parent_window.update_3d_scene()
            
            self.parent_window.statusBar().showMessage("Settings applied successfully", 3000)
    
    def accept(self):
        """Apply settings and close"""
        self.apply_settings()
        super().accept()


class WhatsNewDialog(QDialog):
    """Dialog showing recent changes and improvements"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("What's New")
        self.setModal(False)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("<h2>Recent Updates and Improvements</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Content
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(self.get_changelog_html())
        layout.addWidget(text_edit)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def get_changelog_html(self):
        """Generate HTML for changelog"""
        return """
        <html>
        <body style='font-family: Arial, sans-serif; line-height: 1.6;'>
        
        <h3>🎨 Version 2.0 - Major UI Overhaul</h3>
        <ul>
            <li><b>Enhanced 3D Visualization</b>
                <ul>
                    <li>Dual-layer grid system (major 5m + minor 1m grids)</li>
                    <li>Color-coded coordinate axes (Red=X, Green=Y, Blue=Z)</li>
                    <li>Glow effects on all markers</li>
                    <li>Antialiasing on all lines</li>
                </ul>
            </li>
            <li><b>Dynamic Visual Elements</b>
                <ul>
                    <li>Trail Effect: Orange trail showing last 20 positions</li>
                    <li>Velocity Vector: Green arrow showing speed and direction</li>
                    <li>Target Line: Golden line to current waypoint</li>
                    <li>Waypoint Connections: Cyan lines connecting waypoints</li>
                    <li>Animated Target: Pulsing current waypoint</li>
                </ul>
            </li>
            <li><b>Camera Controls</b>
                <ul>
                    <li>4 Preset Views: Top, Side, Front, Isometric</li>
                    <li>Follow Drone Mode: Camera tracks drone automatically</li>
                    <li>Smooth camera transitions</li>
                </ul>
            </li>
            <li><b>Theme Support</b>
                <ul>
                    <li>White theme for bright environments</li>
                    <li>Black theme for low-light conditions</li>
                    <li>Theme-aware colors for all elements</li>
                </ul>
            </li>
        </ul>
        
        <h3>🆕 Version 1.5 - Dynamic Waypoints</h3>
        <ul>
            <li><b>Real-time Waypoint Modification</b>
                <ul>
                    <li>Add waypoints during flight</li>
                    <li>Modify waypoints on-the-fly</li>
                    <li>Remove waypoints in real-time</li>
                    <li>~3ms trajectory regeneration time</li>
                </ul>
            </li>
            <li><b>Click-to-Add Mode</b>
                <ul>
                    <li>Click on 3D view to add waypoints</li>
                    <li>Configurable height and speed</li>
                    <li>Visual feedback for new waypoints</li>
                </ul>
            </li>
        </ul>
        
        <h3>🚀 Version 1.0 - Core Features</h3>
        <ul>
            <li><b>Physics-Based Trajectory Generation</b>
                <ul>
                    <li>Realistic drone dynamics</li>
                    <li>Acceleration and velocity limits</li>
                    <li>Smooth waypoint transitions</li>
                </ul>
            </li>
            <li><b>ML-Powered Prediction</b>
                <ul>
                    <li>LSTM neural network</li>
                    <li>Time-series trajectory prediction</li>
                    <li>ONNX export for C++ integration</li>
                </ul>
            </li>
            <li><b>3D Visualization</b>
                <ul>
                    <li>Real-time OpenGL rendering</li>
                    <li>Interactive camera controls</li>
                    <li>Rich telemetry display</li>
                </ul>
            </li>
        </ul>
        
        <hr>
        <p><i>For more details, see the documentation files in the workspace folder.</i></p>
        
        </body>
        </html>
        """


class TemplateSelectionDialog(QDialog):
    """Dialog for selecting and configuring trajectory templates"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Trajectory Templates")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.selected_waypoints = None
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("<h2>Select Trajectory Template</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Template list
        list_label = QLabel("<b>Available Templates:</b>")
        layout.addWidget(list_label)
        
        self.template_list = QListWidget()
        self.template_list.setMinimumHeight(200)
        
        # Add templates with descriptions
        templates = [
            ("circle", "Circle - Circular trajectory"),
            ("spiral_ascending", "Spiral (Ascending) - Upward spiral"),
            ("spiral_descending", "Spiral (Descending) - Downward spiral"),
            ("ascend", "Ascend - Vertical climb"),
            ("descend", "Descend - Vertical descent"),
            ("sharp_turn_right", "Sharp Turn (Right) - 90° right turn"),
            ("sharp_turn_left", "Sharp Turn (Left) - 90° left turn"),
            ("s_curve_horizontal", "S-Curve (Horizontal) - Sinusoidal path"),
            ("s_curve_vertical", "S-Curve (Vertical) - Vertical sine wave"),
            ("c_curve_horizontal", "C-Curve (Horizontal) - Arc trajectory"),
            ("c_curve_vertical", "C-Curve (Vertical) - Vertical arc"),
            ("figure_eight", "Figure-Eight - ∞ pattern"),
            ("square", "Square - Rectangular path")
        ]
        
        for template_id, description in templates:
            item = QListWidgetItem(description)
            item.setData(Qt.UserRole, template_id)
            self.template_list.addItem(item)
        
        self.template_list.setCurrentRow(0)
        self.template_list.currentItemChanged.connect(self.on_template_changed)
        layout.addWidget(self.template_list)
        
        # Parameters section
        params_label = QLabel("<b>Parameters:</b>")
        layout.addWidget(params_label)
        
        params_form = QFormLayout()
        
        # Center position
        center_layout = QHBoxLayout()
        self.center_x = QDoubleSpinBox()
        self.center_x.setRange(-100, 100)
        self.center_x.setValue(0)
        self.center_y = QDoubleSpinBox()
        self.center_y.setRange(-100, 100)
        self.center_y.setValue(0)
        self.center_z = QDoubleSpinBox()
        self.center_z.setRange(1, 100)
        self.center_z.setValue(15)
        center_layout.addWidget(QLabel("X:"))
        center_layout.addWidget(self.center_x)
        center_layout.addWidget(QLabel("Y:"))
        center_layout.addWidget(self.center_y)
        center_layout.addWidget(QLabel("Z:"))
        center_layout.addWidget(self.center_z)
        params_form.addRow("Center (m):", center_layout)
        
        # Size/radius
        self.size_spin = QDoubleSpinBox()
        self.size_spin.setRange(5, 100)
        self.size_spin.setValue(20)
        params_form.addRow("Size/Radius (m):", self.size_spin)
        
        # Speed
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(1, 50)
        self.speed_spin.setValue(12)
        params_form.addRow("Speed (m/s):", self.speed_spin)
        
        # Number of points
        self.points_spin = QSpinBox()
        self.points_spin.setRange(5, 100)
        self.points_spin.setValue(20)
        params_form.addRow("Number of Waypoints:", self.points_spin)
        
        layout.addLayout(params_form)
        
        # Description box
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(100)
        layout.addWidget(self.description_text)
        
        # Update description for first template
        self.on_template_changed()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.generate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def on_template_changed(self):
        """Update description when template selection changes"""
        current_item = self.template_list.currentItem()
        if not current_item:
            return
        
        template_id = current_item.data(Qt.UserRole)
        
        descriptions = {
            'circle': "A circular trajectory around a center point. Perfect for orbit patterns.",
            'spiral_ascending': "An ascending spiral that increases in radius and altitude. Great for gaining height while moving outward.",
            'spiral_descending': "A descending spiral that decreases in radius and altitude. Useful for controlled descent.",
            'ascend': "Straight vertical climb to gain altitude quickly.",
            'descend': "Controlled vertical descent to lower altitude.",
            'sharp_turn_right': "L-shaped path with a sharp 90° right turn. Good for testing agility.",
            'sharp_turn_left': "L-shaped path with a sharp 90° left turn.",
            's_curve_horizontal': "Sinusoidal wave pattern in horizontal plane. Tests smooth lateral control.",
            's_curve_vertical': "Sinusoidal wave pattern with vertical oscillations.",
            'c_curve_horizontal': "Partial circular arc (C-shape) in horizontal plane.",
            'c_curve_vertical': "Partial circular arc (C-shape) in vertical plane.",
            'figure_eight': "Figure-eight (∞) pattern. Complex trajectory for testing precision.",
            'square': "Square/rectangular trajectory with four corners. Tests sharp direction changes."
        }
        
        self.description_text.setPlainText(descriptions.get(template_id, ""))
    
    def generate_and_accept(self):
        """Generate waypoints from selected template"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a template.")
            return
        
        template_id = current_item.data(Qt.UserRole)
        
        try:
            # Get parameters
            center = (self.center_x.value(), self.center_y.value(), self.center_z.value())
            size = self.size_spin.value()
            speed = self.speed_spin.value()
            num_points = self.points_spin.value()
            
            # Generate waypoints based on template
            if template_id in ['circle']:
                waypoints = TrajectoryTemplates.get_template(
                    template_id, center=center, radius=size, speed=speed, num_points=num_points
                )
            elif template_id in ['spiral_ascending', 'spiral_descending']:
                waypoints = TrajectoryTemplates.get_template(
                    template_id, center=center, end_radius=size, speed=speed, num_points=num_points
                )
            elif template_id in ['ascend', 'descend']:
                waypoints = TrajectoryTemplates.get_template(
                    template_id, start_pos=center, height_change=size, speed=speed, num_points=num_points
                )
            elif template_id in ['sharp_turn_right', 'sharp_turn_left']:
                waypoints = TrajectoryTemplates.get_template(
                    template_id, start_pos=center, leg_length=size, speed=speed, num_points=num_points
                )
            elif template_id in ['s_curve_horizontal', 's_curve_vertical']:
                waypoints = TrajectoryTemplates.get_template(
                    template_id, start_pos=center, length=size*2, amplitude=size/2, speed=speed, num_points=num_points
                )
            elif template_id in ['c_curve_horizontal', 'c_curve_vertical']:
                waypoints = TrajectoryTemplates.get_template(
                    template_id, start_pos=center, radius=size, speed=speed, num_points=num_points
                )
            elif template_id == 'figure_eight':
                waypoints = TrajectoryTemplates.get_template(
                    template_id, center=center, radius=size, speed=speed, num_points=num_points
                )
            elif template_id == 'square':
                waypoints = TrajectoryTemplates.get_template(
                    template_id, center=center, side_length=size, speed=speed, num_points_per_side=num_points//4
                )
            else:
                waypoints = TrajectoryTemplates.get_template(template_id, speed=speed)
            
            self.selected_waypoints = waypoints
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate template: {str(e)}")


class SaveTrajectoryDialog(QDialog):
    """Dialog for saving current trajectory"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Trajectory")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("<h3>Save Current Trajectory</h3>")
        layout.addWidget(title)
        
        # Form
        form = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("My Trajectory")
        form.addRow("Name:", self.name_input)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Optional description...")
        self.description_input.setMaximumHeight(100)
        form.addRow("Description:", self.description_input)
        
        layout.addLayout(form)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_name(self):
        return self.name_input.text().strip() or "Unnamed Trajectory"
    
    def get_description(self):
        return self.description_input.toPlainText().strip()


class TrajectoryBrowserDialog(QDialog):
    """Dialog for browsing and loading saved trajectories"""
    
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self.storage = storage
        self.selected_trajectory = None
        
        self.setWindowTitle("Browse Saved Trajectories")
        self.setModal(True)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("<h2>Saved Trajectories</h2>")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Name", "Waypoints", "Created", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.doubleClicked.connect(self.load_selected)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        layout.addWidget(self.table)
        
        # Refresh table
        self.refresh_table()
        
        # Info label
        info_label = QLabel("Double-click to load, or select and click Load button")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load")
        self.load_btn.clicked.connect(self.load_selected)
        button_layout.addWidget(self.load_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.clicked.connect(self.delete_selected)
        button_layout.addWidget(self.delete_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_table)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def refresh_table(self):
        """Refresh the trajectory list"""
        trajectories = self.storage.list_trajectories()
        
        self.table.setRowCount(len(trajectories))
        
        for i, traj in enumerate(trajectories):
            # Name
            name_item = QTableWidgetItem(traj['name'])
            name_item.setData(Qt.UserRole, traj['filepath'])
            self.table.setItem(i, 0, name_item)
            
            # Waypoints count
            wp_item = QTableWidgetItem(str(traj['num_waypoints']))
            wp_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, wp_item)
            
            # Created date
            created = traj['created_at'][:10] if traj['created_at'] else "Unknown"
            date_item = QTableWidgetItem(created)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 2, date_item)
            
            # Description
            desc = traj['description'][:100] if traj['description'] else ""
            desc_item = QTableWidgetItem(desc)
            self.table.setItem(i, 3, desc_item)
        
        if len(trajectories) == 0:
            self.table.setRowCount(1)
            item = QTableWidgetItem("No saved trajectories found. Save a trajectory to see it here.")
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, item)
            self.table.setSpan(0, 0, 1, 4)
    
    def load_selected(self):
        """Load the selected trajectory"""
        current_row = self.table.currentRow()
        if current_row < 0 or self.table.rowCount() == 0:
            return
        
        name_item = self.table.item(current_row, 0)
        if not name_item:
            return
        
        filepath = name_item.data(Qt.UserRole)
        if not filepath:
            return
        
        try:
            self.selected_trajectory = self.storage.load_trajectory(filepath)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load trajectory: {str(e)}")
    
    def delete_selected(self):
        """Delete the selected trajectory"""
        current_row = self.table.currentRow()
        if current_row < 0 or self.table.rowCount() == 0:
            return
        
        name_item = self.table.item(current_row, 0)
        if not name_item:
            return
        
        filepath = name_item.data(Qt.UserRole)
        if not filepath:
            return
        
        name = name_item.text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.storage.delete_trajectory(filepath):
                self.refresh_table()
                self.statusBar().showMessage(f"Deleted '{name}'", 3000) if hasattr(self, 'statusBar') else None
            else:
                QMessageBox.warning(self, "Error", "Failed to delete trajectory")


class DroneSimulationWindow(QMainWindow):
    """Main simulation window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drone Trajectory Simulation Pro")
        self.setGeometry(100, 100, 1800, 950)
        
        # ========== SETTINGS ==========
        # Visual Options
        self.show_trail = False
        self.show_velocity = False
        self.show_connections = False
        self.show_target_line = False
        self.follow_drone_enabled = False
        self.trail_length = 20  # Number of points to show in trail
        
        # Theme Settings
        self.current_theme = 'white'  # 'white' or 'black'
        
        # Playback Settings
        self.playback_speed = 1.0
        self.auto_play_enabled = True  # Auto-play when waypoints are added
        
        # Waypoint Settings
        self.click_height = 10.0  # Default height for clicked waypoints (m)
        self.click_speed = 10.0  # Default speed for clicked waypoints (m/s)
        # ========== END SETTINGS ==========
        
        # Initialize components
        self.trajectory_generator = TrajectoryGenerator(dt=0.1)
        self.trajectory_storage = TrajectoryStorage()  # For saving/loading trajectories
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
        
        # Waypoint management
        self.user_waypoints = []  # List of dicts: [{'position': [x,y,z], 'speed': float}, ...]
        self.click_mode_enabled = False
        self.dynamic_mode_enabled = False  # Allow waypoint changes during flight
        self.visited_waypoints = set()  # Track visited waypoints
        
        # Setup UI
        self.setup_ui()
        self.setup_menu_bar()
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
<span style='color: #00cccc;'>●</span> <b>Trajectory WP</b> (Cyan)<br>
<span style='color: #b933cc;'>●</span> <b>User WP</b> (Purple)<br>
<span style='color: #33cc33;'>●</span> <b>Visited</b> (Green)<br>
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
        
        # Height control for clicked waypoints - using text box
        height_layout = QHBoxLayout()
        height_layout.setSpacing(8)
        height_lbl = QLabel("Height (m):")
        height_lbl.setObjectName("controlLabel")
        height_layout.addWidget(height_lbl)
        
        self.height_input = QLineEdit()
        self.height_input.setText("10")
        self.height_input.setMaximumWidth(80)
        self.height_input.setPlaceholderText("10")
        self.height_input.textChanged.connect(self.update_click_height_from_text)
        height_layout.addWidget(self.height_input)
        waypoint_layout.addLayout(height_layout)
        
        # Speed control for clicked waypoints - using text box
        speed_layout = QHBoxLayout()
        speed_layout.setSpacing(8)
        speed_lbl = QLabel("Speed (m/s):")
        speed_lbl.setObjectName("controlLabel")
        speed_layout.addWidget(speed_lbl)
        
        self.waypoint_speed_input = QLineEdit()
        self.waypoint_speed_input.setText("10")
        self.waypoint_speed_input.setMaximumWidth(80)
        self.waypoint_speed_input.setPlaceholderText("10")
        self.waypoint_speed_input.textChanged.connect(self.update_click_speed_from_text)
        speed_layout.addWidget(self.waypoint_speed_input)
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
        
        # Template and Save/Load buttons
        template_btn_layout = QVBoxLayout()
        template_btn_layout.setSpacing(6)
        
        self.template_btn = QPushButton("✨ Load Template")
        self.template_btn.clicked.connect(self.load_template)
        self.template_btn.setObjectName("templateButton")
        self.template_btn.setMinimumHeight(38)
        self.template_btn.setToolTip("Load pre-defined trajectory pattern")
        template_btn_layout.addWidget(self.template_btn)
        
        # Save/Load buttons row
        save_load_layout = QHBoxLayout()
        save_load_layout.setSpacing(6)
        
        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self.save_trajectory)
        self.save_btn.setMinimumHeight(34)
        self.save_btn.setObjectName("saveButton")
        self.save_btn.setToolTip("Save current trajectory")
        save_load_layout.addWidget(self.save_btn)
        
        self.load_btn = QPushButton("📂 Load")
        self.load_btn.clicked.connect(self.browse_trajectories)
        self.load_btn.setMinimumHeight(34)
        self.load_btn.setObjectName("loadButton")
        self.load_btn.setToolTip("Browse saved trajectories")
        save_load_layout.addWidget(self.load_btn)
        
        template_btn_layout.addLayout(save_load_layout)
        waypoint_layout.addLayout(template_btn_layout)
        
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
    
    def setup_menu_bar(self):
        """Setup the menu bar with File, Settings, and Help menus"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        # Trajectory sub-menu
        trajectory_menu = file_menu.addMenu("📁 Trajectory")
        
        save_traj_action = QAction("💾 Save Trajectory...", self)
        save_traj_action.setShortcut("Ctrl+S")
        save_traj_action.setStatusTip("Save current trajectory")
        save_traj_action.triggered.connect(self.save_trajectory)
        trajectory_menu.addAction(save_traj_action)
        
        load_traj_action = QAction("📂 Browse Trajectories...", self)
        load_traj_action.setShortcut("Ctrl+O")
        load_traj_action.setStatusTip("Browse and load saved trajectories")
        load_traj_action.triggered.connect(self.browse_trajectories)
        trajectory_menu.addAction(load_traj_action)
        
        trajectory_menu.addSeparator()
        
        template_action = QAction("✨ Load Template...", self)
        template_action.setShortcut("Ctrl+T")
        template_action.setStatusTip("Load pre-defined trajectory template")
        template_action.triggered.connect(self.load_template)
        trajectory_menu.addAction(template_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Settings Menu
        settings_menu = menubar.addMenu("&Settings")
        
        preferences_action = QAction("&Preferences...", self)
        preferences_action.setShortcut("Ctrl+,")
        preferences_action.setStatusTip("Open settings dialog")
        preferences_action.triggered.connect(self.open_settings)
        settings_menu.addAction(preferences_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        whats_new_action = QAction("&What's New", self)
        whats_new_action.setStatusTip("View recent changes and improvements")
        whats_new_action.triggered.connect(self.open_whats_new)
        help_menu.addAction(whats_new_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def open_settings(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def open_whats_new(self):
        """Open the What's New dialog"""
        dialog = WhatsNewDialog(self)
        dialog.show()
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Drone Trajectory Simulation Pro</h2>
        <p><b>Version 2.1</b></p>
        <p>A comprehensive ML-powered drone trajectory prediction system with 
        physics-based simulation, 3D visualization, and real-time inference capabilities.</p>
        <br>
        <p><b>Features:</b></p>
        <ul>
            <li>Physics-based trajectory generation</li>
            <li>LSTM neural network prediction</li>
            <li>Real-time 3D visualization</li>
            <li>Dynamic waypoint modification</li>
            <li>Save/Load trajectories</li>
            <li>Pre-defined trajectory templates</li>
            <li>Multiple themes and visual options</li>
            <li>ONNX export for C++ integration</li>
        </ul>
        <br>
        <p><i>For documentation, see the README.md and other docs in the workspace folder.</i></p>
        """
        QMessageBox.about(self, "About Drone Simulation", about_text)
    
    def save_trajectory(self):
        """Save current trajectory to file"""
        if not self.user_waypoints:
            QMessageBox.warning(self, "No Waypoints", 
                              "Please add waypoints before saving a trajectory.")
            return
        
        dialog = SaveTrajectoryDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_name()
            description = dialog.get_description()
            
            try:
                filepath = self.trajectory_storage.save_trajectory(
                    self.user_waypoints,
                    name,
                    description
                )
                QMessageBox.information(self, "Success", 
                                      f"Trajectory saved successfully!\n\nFile: {os.path.basename(filepath)}")
                self.statusBar().showMessage(f"Saved trajectory: {name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save trajectory: {str(e)}")
    
    def browse_trajectories(self):
        """Browse and load saved trajectories"""
        dialog = TrajectoryBrowserDialog(self.trajectory_storage, self)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.selected_trajectory:
                self.load_trajectory_from_data(dialog.selected_trajectory)
    
    def load_trajectory_from_data(self, trajectory_data):
        """Load trajectory from loaded data"""
        try:
            waypoints = trajectory_data['waypoints']
            name = trajectory_data.get('name', 'Loaded Trajectory')
            
            # Clear current waypoints
            self.user_waypoints = []
            
            # Add loaded waypoints
            for wp in waypoints:
                self.user_waypoints.append(wp)
            
            # Update UI
            self.update_waypoint_list()
            self.update_user_waypoint_markers()
            self.update_3d_scene()
            
            # Generate trajectory if auto-play is enabled
            if self.auto_play_enabled:
                self.generate_from_waypoints()
            
            self.statusBar().showMessage(f"Loaded trajectory: {name} ({len(waypoints)} waypoints)", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load trajectory: {str(e)}")
    
    def load_template(self):
        """Load pre-defined trajectory template"""
        dialog = TemplateSelectionDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            if dialog.selected_waypoints:
                # Clear current waypoints
                self.user_waypoints = []
                
                # Add template waypoints
                for wp in dialog.selected_waypoints:
                    self.user_waypoints.append(wp)
                
                # Update UI
                self.update_waypoint_list()
                self.update_user_waypoint_markers()
                self.update_3d_scene()
                
                # Generate trajectory if auto-play is enabled
                if self.auto_play_enabled:
                    self.generate_from_waypoints()
                
                self.statusBar().showMessage(
                    f"Loaded template with {len(dialog.selected_waypoints)} waypoints", 
                    3000
                )
    
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
        
        # Update waypoint marker colors
        self.update_waypoint_colors()
        
        # Update user waypoint marker colors
        self.update_user_waypoint_markers()
        
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
            
            /* Play button - green accent (standard play convention) */
            QPushButton#playButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66bb6a, stop:1 #4caf50);
            }
            
            QPushButton#playButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7bc67e, stop:1 #66bb6a);
                border: 1px solid #43a047;
            }
            
            /* Remove button - red accent (destructive action warning) */
            QPushButton#removeButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef5350, stop:1 #f44336);
            }
            
            QPushButton#removeButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e57373, stop:1 #ef5350);
                border: 1px solid #e53935;
            }
            
            /* Disabled button styling */
            QPushButton#applyButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #bdbdbd, stop:1 #9e9e9e);
                color: #e0e0e0;
                border: 1px solid #757575;
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
                border: 2px solid #757575;
                background: #fafafa;
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #3498db;
                background: #e8f4fd;
            }
            
            QCheckBox::indicator:checked {
                background: #3498db;
                border: 2px solid #2980b9;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cGF0aCBkPSJNMTMgNEw2IDExTDMgOCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4=);
            }
            
            QCheckBox::indicator:checked:hover {
                background: #5dade2;
                border: 2px solid #2980b9;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cGF0aCBkPSJNMTMgNEw2IDExTDMgOCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4=);
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
            
            /* Play button - green accent (standard play convention) */
            QPushButton#playButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a8f4a, stop:1 #357a38);
            }
            
            QPushButton#playButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5a9f5a, stop:1 #458a48);
                border: 1px solid #2d6a30;
            }
            
            /* Remove button - red accent (destructive action warning) */
            QPushButton#removeButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #bf3530, stop:1 #a42a26);
            }
            
            QPushButton#removeButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #cf4540, stop:1 #b43a36);
                border: 1px solid #941f1e;
            }
            
            /* Disabled button styling */
            QPushButton#applyButton:disabled {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a4a4a, stop:1 #3a3a3a);
                color: #7a7a7a;
                border: 1px solid #2a2a2a;
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
                border: 2px solid #808080;
                background: #3a3a3a;
            }
            
            QCheckBox::indicator:hover {
                border: 2px solid #4a7ba7;
                background: #4a4a4a;
            }
            
            QCheckBox::indicator:checked {
                background: #4a7ba7;
                border: 2px solid #5a8bb7;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cGF0aCBkPSJNMTMgNEw2IDExTDMgOCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4=);
            }
            
            QCheckBox::indicator:checked:hover {
                background: #5a8bb7;
                border: 2px solid #6a9bc7;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cGF0aCBkPSJNMTMgNEw2IDExTDMgOCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4=);
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
        
        # Waypoint markers with glow - BRIGHT CYAN/TEAL (NOT white) - theme-compliant
        self.waypoint_markers_glow = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.0, 0.6, 0.6, 0.3),  # Bright cyan glow (NOT white)
            size=22,
            pxMode=True
        )
        self.plot_widget.addItem(self.waypoint_markers_glow)
        
        self.waypoint_markers = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.0, 0.6, 0.6, 1.0),  # Bright cyan (NOT white)
            size=14,
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
        
        # User waypoint markers with glow - BRIGHT PURPLE (NOT white) - theme-compliant
        self.user_waypoint_markers_glow = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.7, 0.2, 0.8, 0.3),  # Bright purple glow (NOT white)
            size=24,
            pxMode=True
        )
        self.plot_widget.addItem(self.user_waypoint_markers_glow)
        
        self.user_waypoint_markers = gl.GLScatterPlotItem(
            pos=np.array([[0, 0, 0]]),
            color=(0.7, 0.2, 0.8, 1.0),  # Bright purple (NOT white)
            size=16,
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
        # Main body - top plate (octagonal for modern look)
        top_plate = self.create_octagonal_plate(radius=1.0, thickness=0.1)
        self.drone_body_top = gl.GLMeshItem(
            meshdata=top_plate,
            color=(0.15, 0.15, 0.18, 1.0),  # Dark carbon fiber look
            smooth=True,
            shader='shaded',
            glOptions='opaque'
        )
        self.plot_widget.addItem(self.drone_body_top)
        
        # Bottom plate (slightly smaller)
        bottom_plate = self.create_octagonal_plate(radius=0.85, thickness=0.08)
        self.drone_body_bottom = gl.GLMeshItem(
            meshdata=bottom_plate,
            color=(0.12, 0.12, 0.15, 1.0),  # Slightly darker
            smooth=True,
            shader='shaded',
            glOptions='opaque'
        )
        self.plot_widget.addItem(self.drone_body_bottom)
        
        # Central hub (rounded cylinder connecting plates)
        hub = gl.MeshData.cylinder(rows=10, cols=20, radius=[0.5, 0.5], length=0.4)
        self.drone_hub = gl.GLMeshItem(
            meshdata=hub,
            color=(0.20, 0.60, 0.86, 1.0),  # Modern blue accent
            smooth=True,
            shader='shaded',
            glOptions='opaque'
        )
        self.plot_widget.addItem(self.drone_hub)
        
        # Battery indicator LEDs on top
        self.battery_leds = []
        for i in range(4):
            led = gl.MeshData.sphere(rows=6, cols=6, radius=0.08)
            led_item = gl.GLMeshItem(
                meshdata=led,
                color=(0.0, 1.0, 0.3, 1.0),  # Green LEDs
                smooth=True,
                shader='shaded',
                glOptions='opaque'
            )
            self.plot_widget.addItem(led_item)
            self.battery_leds.append(led_item)
        
        # Drone arms (4 modern angular arms)
        self.drone_arms = []
        arm_positions = [
            (1, 0, 0),   # Front
            (-1, 0, 0),  # Back
            (0, 1, 0),   # Right
            (0, -1, 0)   # Left
        ]
        
        for pos in arm_positions:
            # Create modern arm mesh (rectangular with taper)
            arm_mesh = self.create_tapered_arm(length=2.2, width=0.25, height=0.15)
            arm = gl.GLMeshItem(
                meshdata=arm_mesh,
                color=(0.18, 0.18, 0.20, 1.0),  # Dark gray
                smooth=True,
                shader='shaded',
                glOptions='opaque'
            )
            self.drone_arms.append((arm, pos))
            self.plot_widget.addItem(arm)
        
        # Motor housings (at end of each arm)
        self.motor_housings = []
        for pos in arm_positions:
            motor = gl.MeshData.cylinder(rows=10, cols=20, radius=[0.35, 0.35], length=0.4)
            motor_item = gl.GLMeshItem(
                meshdata=motor,
                color=(0.25, 0.25, 0.28, 1.0),  # Slightly lighter gray
                smooth=True,
                shader='shaded',
                glOptions='opaque'
            )
            self.plot_widget.addItem(motor_item)
            self.motor_housings.append((motor_item, pos))
        
        # LED strips on arms (RGB accent lights)
        self.arm_leds = []
        colors = [
            (1.0, 0.0, 0.0, 0.9),  # Front - Red
            (0.0, 1.0, 0.0, 0.9),  # Back - Green
            (0.0, 0.5, 1.0, 0.9),  # Right - Blue
            (1.0, 1.0, 0.0, 0.9)   # Left - Yellow
        ]
        for i, pos in enumerate(arm_positions):
            led = self.create_led_strip(length=1.8, width=0.15, height=0.05)
            led_item = gl.GLMeshItem(
                meshdata=led,
                color=colors[i],
                smooth=True,
                shader='shaded',
                glOptions='translucent'
            )
            self.plot_widget.addItem(led_item)
            self.arm_leds.append((led_item, pos))
        
        # Camera gimbal (underneath center)
        gimbal_body = gl.MeshData.sphere(rows=10, cols=10, radius=0.35)
        self.gimbal = gl.GLMeshItem(
            meshdata=gimbal_body,
            color=(0.1, 0.1, 0.12, 1.0),  # Very dark
            smooth=True,
            shader='shaded',
            glOptions='opaque'
        )
        self.plot_widget.addItem(self.gimbal)
        
        # Camera lens (front of gimbal)
        lens = gl.MeshData.cylinder(rows=8, cols=16, radius=[0.15, 0.15], length=0.2)
        self.camera_lens = gl.GLMeshItem(
            meshdata=lens,
            color=(0.05, 0.05, 0.08, 1.0),  # Almost black
            smooth=True,
            shader='shaded',
            glOptions='opaque'
        )
        self.plot_widget.addItem(self.camera_lens)
        
        # Landing gear (4 legs)
        self.landing_gear = []
        for pos in arm_positions:
            leg = self.create_landing_leg(length=0.8, radius=0.08)
            leg_item = gl.GLMeshItem(
                meshdata=leg,
                color=(0.15, 0.15, 0.17, 1.0),
                smooth=True,
                shader='shaded',
                glOptions='opaque'
            )
            self.plot_widget.addItem(leg_item)
            self.landing_gear.append((leg_item, pos))
        
        # Antenna (on top)
        antenna = gl.MeshData.cylinder(rows=4, cols=8, radius=[0.03, 0.02], length=0.6)
        self.antenna = gl.GLMeshItem(
            meshdata=antenna,
            color=(0.8, 0.8, 0.85, 1.0),  # Metallic silver
            smooth=True,
            shader='shaded',
            glOptions='opaque'
        )
        self.plot_widget.addItem(self.antenna)
        
        # Propellers (4 sets of 3 blades each for more realism)
        self.propellers = []
        for pos in arm_positions:
            # Three blades per propeller
            blade1 = self.create_curved_propeller_blade()
            blade2 = self.create_curved_propeller_blade()
            blade3 = self.create_curved_propeller_blade()
            
            blade1_item = gl.GLMeshItem(
                meshdata=blade1,
                color=(0.08, 0.08, 0.10, 0.85),  # Dark translucent
                smooth=True,
                shader='shaded',
                glOptions='translucent'
            )
            blade2_item = gl.GLMeshItem(
                meshdata=blade2,
                color=(0.08, 0.08, 0.10, 0.85),
                smooth=True,
                shader='shaded',
                glOptions='translucent'
            )
            blade3_item = gl.GLMeshItem(
                meshdata=blade3,
                color=(0.08, 0.08, 0.10, 0.85),
                smooth=True,
                shader='shaded',
                glOptions='translucent'
            )
            
            self.plot_widget.addItem(blade1_item)
            self.plot_widget.addItem(blade2_item)
            self.plot_widget.addItem(blade3_item)
            
            # Propeller hub (center)
            hub = gl.MeshData.sphere(rows=6, cols=6, radius=0.12)
            hub_item = gl.GLMeshItem(
                meshdata=hub,
                color=(0.15, 0.15, 0.18, 1.0),
                smooth=True,
                shader='shaded',
                glOptions='opaque'
            )
            self.plot_widget.addItem(hub_item)
            
            # Store blade items with their position
            self.propellers.append({
                'blade1': blade1_item,
                'blade2': blade2_item,
                'blade3': blade3_item,
                'hub': hub_item,
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
    
    def create_octagonal_plate(self, radius=1.0, thickness=0.1):
        """Create an octagonal plate for drone body"""
        verts = []
        faces = []
        
        # Top octagon
        for i in range(8):
            angle = 2 * np.pi * i / 8
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            verts.append([x, y, thickness/2])
        
        # Bottom octagon
        for i in range(8):
            angle = 2 * np.pi * i / 8
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            verts.append([x, y, -thickness/2])
        
        # Top cap (triangles from center)
        center_top = len(verts)
        verts.append([0, 0, thickness/2])
        for i in range(8):
            next_i = (i + 1) % 8
            faces.append([center_top, i, next_i])
        
        # Bottom cap
        center_bottom = len(verts)
        verts.append([0, 0, -thickness/2])
        for i in range(8):
            next_i = (i + 1) % 8
            faces.append([center_bottom, next_i + 8, i + 8])
        
        # Sides
        for i in range(8):
            next_i = (i + 1) % 8
            faces.append([i, next_i, next_i + 8])
            faces.append([i, next_i + 8, i + 8])
        
        verts = np.array(verts)
        faces = np.array(faces)
        
        return gl.MeshData(vertexes=verts, faces=faces)
    
    def create_tapered_arm(self, length=2.2, width=0.25, height=0.15):
        """Create a tapered rectangular arm"""
        half_w = width / 2
        half_h = height / 2
        
        # Wider at base, narrower at tip
        base_w = half_w
        tip_w = half_w * 0.6
        
        verts = np.array([
            # Base (near body) - 4 corners
            [-length/8, -base_w, half_h],
            [-length/8, base_w, half_h],
            [-length/8, base_w, -half_h],
            [-length/8, -base_w, -half_h],
            # Tip (motor end) - 4 corners
            [length*7/8, -tip_w, half_h],
            [length*7/8, tip_w, half_h],
            [length*7/8, tip_w, -half_h],
            [length*7/8, -tip_w, -half_h],
        ])
        
        faces = np.array([
            # Top face
            [0, 1, 5], [0, 5, 4],
            # Bottom face
            [3, 7, 6], [3, 6, 2],
            # Front face
            [1, 2, 6], [1, 6, 5],
            # Back face
            [0, 4, 7], [0, 7, 3],
            # Left face
            [0, 3, 2], [0, 2, 1],
            # Right face
            [4, 5, 6], [4, 6, 7],
        ])
        
        return gl.MeshData(vertexes=verts, faces=faces)
    
    def create_led_strip(self, length=1.8, width=0.15, height=0.05):
        """Create an LED strip for arm lighting"""
        half_w = width / 2
        half_h = height / 2
        
        verts = np.array([
            # Top surface
            [0, -half_w, half_h],
            [length, -half_w, half_h],
            [length, half_w, half_h],
            [0, half_w, half_h],
            # Bottom surface
            [0, -half_w, -half_h],
            [length, -half_w, -half_h],
            [length, half_w, -half_h],
            [0, half_w, -half_h],
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
        
        return gl.MeshData(vertexes=verts, faces=faces)
    
    def create_landing_leg(self, length=0.8, radius=0.08):
        """Create a curved landing leg"""
        segments = 12
        verts = []
        faces = []
        
        # Create curved leg path
        for i in range(segments):
            t = i / (segments - 1)
            # Curved path: starts vertical, curves outward
            x = 0.3 * t  # Outward
            y = 0
            z = -length * t  # Downward
            
            # Create ring at this position
            for j in range(8):
                angle = 2 * np.pi * j / 8
                vx = x + radius * np.cos(angle)
                vy = y + radius * np.sin(angle)
                verts.append([vx, vy, z])
        
        # Create faces between rings
        for i in range(segments - 1):
            for j in range(8):
                next_j = (j + 1) % 8
                v1 = i * 8 + j
                v2 = i * 8 + next_j
                v3 = (i + 1) * 8 + next_j
                v4 = (i + 1) * 8 + j
                faces.append([v1, v2, v3])
                faces.append([v1, v3, v4])
        
        verts = np.array(verts)
        faces = np.array(faces)
        
        return gl.MeshData(vertexes=verts, faces=faces)
    
    def create_curved_propeller_blade(self):
        """Create a curved propeller blade with realistic airfoil shape"""
        # More realistic blade with airfoil cross-section
        segments = 10
        verts = []
        faces = []
        
        for i in range(segments):
            t = i / (segments - 1)
            # Blade spans from hub to tip
            x = -0.05 + 1.3 * t  # Blade length
            
            # Width tapers from hub to tip
            width = 0.2 * (1.0 - 0.7 * t)
            
            # Airfoil thickness (thicker at root, thinner at tip)
            thick_top = 0.08 * (1.0 - 0.8 * t)
            thick_bottom = 0.03 * (1.0 - 0.8 * t)
            
            # Twist angle (more pitch at hub, less at tip)
            twist = 0.15 * (1.0 - t)
            
            # Top surface vertex
            verts.append([x, -width, thick_top * np.cos(twist)])
            # Bottom surface vertex
            verts.append([x, -width, -thick_bottom * np.cos(twist)])
            # Top surface vertex (other side)
            verts.append([x, width, thick_top * np.cos(twist)])
            # Bottom surface vertex (other side)
            verts.append([x, width, -thick_bottom * np.cos(twist)])
        
        # Create faces
        for i in range(segments - 1):
            base = i * 4
            next_base = (i + 1) * 4
            
            # Top surface
            faces.append([base, base + 2, next_base + 2])
            faces.append([base, next_base + 2, next_base])
            
            # Bottom surface
            faces.append([base + 1, next_base + 3, base + 3])
            faces.append([base + 1, next_base + 1, next_base + 3])
            
            # Leading edge
            faces.append([base, base + 1, next_base + 1])
            faces.append([base, next_base + 1, next_base])
            
            # Trailing edge
            faces.append([base + 2, next_base + 2, next_base + 3])
            faces.append([base + 2, next_base + 3, base + 3])
        
        # Tip cap
        last_base = (segments - 1) * 4
        faces.append([last_base, last_base + 2, last_base + 3])
        faces.append([last_base, last_base + 3, last_base + 1])
        
        verts = np.array(verts)
        faces = np.array(faces)
        
        return gl.MeshData(vertexes=verts, faces=faces)
    
    def update_drone_model_position(self, position, velocity):
        """Update drone model position and orientation"""
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
        
        # Update body plates - top plate
        transform_top = np.eye(4)
        transform_top[:3, 3] = [position[0], position[1], position[2] + 0.2]
        self.drone_body_top.setTransform(transform_top)
        
        # Update body plates - bottom plate
        transform_bottom = np.eye(4)
        transform_bottom[:3, 3] = [position[0], position[1], position[2] - 0.15]
        self.drone_body_bottom.setTransform(transform_bottom)
        
        # Update central hub
        hub_transform = np.eye(4)
        hub_transform[:3, 3] = position
        self.drone_hub.setTransform(hub_transform)
        
        # Update battery LEDs on top (arranged in a row)
        led_spacing = 0.3
        for i, led in enumerate(self.battery_leds):
            led_transform = np.eye(4)
            offset_x = (i - 1.5) * led_spacing
            led_transform[:3, 3] = [position[0] + offset_x, position[1], position[2] + 0.35]
            led.setTransform(led_transform)
        
        # Update arms
        for arm, arm_pos in self.drone_arms:
            # Rotate arm position based on yaw
            angle = np.arctan2(arm_pos[1], arm_pos[0])
            rotated_angle = angle + yaw
            
            arm_world_x = position[0] + 0.5 * np.cos(rotated_angle)
            arm_world_y = position[1] + 0.5 * np.sin(rotated_angle)
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
        
        # Update motor housings (at end of arms)
        for motor, motor_pos in self.motor_housings:
            angle = np.arctan2(motor_pos[1], motor_pos[0])
            rotated_angle = angle + yaw
            
            motor_world_x = position[0] + 2.4 * np.cos(rotated_angle)
            motor_world_y = position[1] + 2.4 * np.sin(rotated_angle)
            motor_world_z = position[2]
            
            motor_transform = np.eye(4)
            motor_transform[:3, 3] = [motor_world_x, motor_world_y, motor_world_z]
            motor.setTransform(motor_transform)
        
        # Update LED strips on arms
        for led, led_pos in self.arm_leds:
            angle = np.arctan2(led_pos[1], led_pos[0])
            rotated_angle = angle + yaw
            
            led_world_x = position[0] + 0.7 * np.cos(rotated_angle)
            led_world_y = position[1] + 0.7 * np.sin(rotated_angle)
            led_world_z = position[2] + 0.05
            
            led_transform = np.eye(4)
            # Rotation
            c = np.cos(rotated_angle)
            s = np.sin(rotated_angle)
            led_transform[0, 0] = c
            led_transform[0, 1] = -s
            led_transform[1, 0] = s
            led_transform[1, 1] = c
            # Position
            led_transform[:3, 3] = [led_world_x, led_world_y, led_world_z]
            led.setTransform(led_transform)
        
        # Update camera gimbal (underneath center, tilts with velocity)
        gimbal_transform = np.eye(4)
        gimbal_transform[:3, 3] = [position[0], position[1], position[2] - 0.5]
        self.gimbal.setTransform(gimbal_transform)
        
        # Update camera lens (points forward, tilts down slightly)
        lens_transform = np.eye(4)
        # Rotate to point forward
        lens_transform[0, 0] = 0
        lens_transform[0, 1] = 1
        lens_transform[1, 0] = -1
        lens_transform[1, 1] = 0
        lens_transform[:3, 3] = [position[0] + 0.25, position[1], position[2] - 0.5]
        self.camera_lens.setTransform(lens_transform)
        
        # Update landing gear
        for leg, leg_pos in self.landing_gear:
            angle = np.arctan2(leg_pos[1], leg_pos[0])
            rotated_angle = angle + yaw
            
            leg_world_x = position[0] + 0.8 * np.cos(rotated_angle)
            leg_world_y = position[1] + 0.8 * np.sin(rotated_angle)
            leg_world_z = position[2] - 0.2
            
            leg_transform = np.eye(4)
            leg_transform[:3, 3] = [leg_world_x, leg_world_y, leg_world_z]
            leg.setTransform(leg_transform)
        
        # Update antenna (on top)
        antenna_transform = np.eye(4)
        antenna_transform[:3, 3] = [position[0], position[1], position[2] + 0.35]
        self.antenna.setTransform(antenna_transform)
        
        # Update propellers with rotation (faster for more realism)
        self.propeller_rotation += 45.0  # Degrees per frame (faster spin)
        if self.propeller_rotation > 360:
            self.propeller_rotation -= 360
        
        for i, prop in enumerate(self.propellers):
            arm_pos = prop['position']
            
            # Calculate propeller world position (at motor location)
            angle = np.arctan2(arm_pos[1], arm_pos[0])
            rotated_angle = angle + yaw
            
            prop_world_x = position[0] + 2.4 * np.cos(rotated_angle)
            prop_world_y = position[1] + 2.4 * np.sin(rotated_angle)
            prop_world_z = position[2] + 0.25
            
            # Propeller hub
            hub_transform = np.eye(4)
            hub_transform[:3, 3] = [prop_world_x, prop_world_y, prop_world_z]
            prop['hub'].setTransform(hub_transform)
            
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
            
            # Blade 2 rotation (120 degrees offset for 3-blade prop)
            blade2_transform = np.eye(4)
            rot_angle2 = np.radians(self.propeller_rotation + 120)
            c2 = np.cos(rot_angle2)
            s2 = np.sin(rot_angle2)
            blade2_transform[0, 0] = c2
            blade2_transform[0, 1] = -s2
            blade2_transform[1, 0] = s2
            blade2_transform[1, 1] = c2
            blade2_transform[:3, 3] = [prop_world_x, prop_world_y, prop_world_z]
            prop['blade2'].setTransform(blade2_transform)
            
            # Blade 3 rotation (240 degrees offset)
            blade3_transform = np.eye(4)
            rot_angle3 = np.radians(self.propeller_rotation + 240)
            c3 = np.cos(rot_angle3)
            s3 = np.sin(rot_angle3)
            blade3_transform[0, 0] = c3
            blade3_transform[0, 1] = -s3
            blade3_transform[1, 0] = s3
            blade3_transform[1, 1] = c3
            blade3_transform[:3, 3] = [prop_world_x, prop_world_y, prop_world_z]
            prop['blade3'].setTransform(blade3_transform)
    
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
    
    def update_click_height_from_text(self, text):
        """Update the height for clicked waypoints from text input"""
        try:
            value = float(text) if text else 10.0
            # Clamp value between reasonable bounds
            value = max(1.0, min(100.0, value))
            self.click_height = value
        except ValueError:
            # If invalid input, keep current value
            pass
    
    def update_click_speed_from_text(self, text):
        """Update the speed for clicked waypoints from text input"""
        try:
            value = float(text) if text else 10.0
            # Clamp value between reasonable bounds
            value = max(0.1, min(50.0, value))
            self.click_speed = value
        except ValueError:
            # If invalid input, keep current value
            pass
    
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
        """Clear all waypoints and trajectory"""
        if self.user_waypoints or self.current_trajectory is not None:
            reply = QMessageBox.question(self, 'Clear Waypoints', 
                                        'Are you sure you want to clear all waypoints and trajectory?',
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Clear user waypoints
                self.user_waypoints.clear()
                self.waypoint_list.clear()
                
                # Clear current trajectory
                self.current_trajectory = None
                self.current_step = 0
                self.is_playing = False
                self.play_btn.setText("▶ Play")
                self.timer.stop()
                
                # Clear visited waypoints
                self.visited_waypoints.clear()
                
                # Clear all 3D visualization elements
                self.trajectory_line.setData(pos=np.array([[0, 0, 0]]))
                self.trail_line.setData(pos=np.array([[0, 0, 0]]))
                self.waypoint_markers.setData(pos=np.array([[1000, 1000, 1000]]))
                self.waypoint_markers_glow.setData(pos=np.array([[1000, 1000, 1000]]))
                self.target_waypoint_marker.setData(pos=np.array([[1000, 1000, 1000]]))
                self.waypoint_connections.setData(pos=np.array([[0, 0, 0]]))
                self.target_line.setData(pos=np.array([[0, 0, 0], [0, 0, 0]]))
                self.velocity_vector.setData(pos=np.array([[0, 0, 0], [0, 0, 0]]))
                
                # Clear waypoint labels
                for text_item in self.waypoint_text_items:
                    self.plot_widget.removeItem(text_item)
                self.waypoint_text_items.clear()
                
                # Update user waypoint markers
                self.update_user_waypoint_markers()
                
                # Reset drone to origin
                initial_pos = np.array([0, 0, 5])
                initial_vel = np.array([0, 0, 0])
                self.update_drone_model_position(initial_pos, initial_vel)
                
                # Reset info labels
                for key in self.info_labels:
                    self.info_labels[key].setText("N/A")
                
                self.statusBar().showMessage("All waypoints and trajectory cleared", 2000)
    
    def update_user_waypoint_markers(self):
        """Update the visual markers for user waypoints - BRIGHT PURPLE (NOT white) - theme-compliant"""
        if self.user_waypoints:
            positions = np.array([wp['position'] for wp in self.user_waypoints])
            
            # BRIGHT, VIVID purple colors (NOT white) - theme-compliant
            if self.current_theme == 'white':
                color = (0.7, 0.2, 0.8, 1.0)         # Bright purple (NOT white)
                glow_color = (0.7, 0.2, 0.8, 0.3)
            else:
                color = (0.85, 0.3, 0.95, 1.0)       # Maximum bright purple for dark background (NOT white)
                glow_color = (0.85, 0.3, 0.95, 0.3)
            
            # Explicitly set size for visibility
            self.user_waypoint_markers.setData(pos=positions, color=color, size=16)
            self.user_waypoint_markers_glow.setData(pos=positions, color=glow_color, size=24)
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
        """Update waypoint colors based on visited status - theme-compliant with BRIGHT colors"""
        if self.current_trajectory is None:
            return
        
        waypoints = self.current_trajectory['waypoints']
        num_waypoints = len(waypoints)
        
        # Create color array for each waypoint
        colors = np.zeros((num_waypoints, 4))
        colors_glow = np.zeros((num_waypoints, 4))
        
        # BRIGHT, VIVID colors that are NEVER white - theme-compliant
        if self.current_theme == 'white':
            # White theme colors - VIBRANT and SATURATED
            visited_color = [0.2, 0.8, 0.2, 1.0]       # Bright green for visited (NOT white)
            visited_glow = [0.2, 0.8, 0.2, 0.3]
            unvisited_color = [0.0, 0.6, 0.6, 1.0]     # Vibrant cyan/teal for unvisited (NOT white)
            unvisited_glow = [0.0, 0.6, 0.6, 0.3]
        else:
            # Black theme colors - MAXIMUM brightness for visibility
            visited_color = [0.3, 1.0, 0.3, 1.0]       # Maximum bright green for visited (NOT white)
            visited_glow = [0.3, 1.0, 0.3, 0.3]
            unvisited_color = [0.0, 0.9, 0.9, 1.0]     # Maximum bright cyan for unvisited (NOT white)
            unvisited_glow = [0.0, 0.9, 0.9, 0.3]
        
        for i in range(num_waypoints):
            if i in self.visited_waypoints:
                colors[i] = visited_color
                colors_glow[i] = visited_glow
            else:
                colors[i] = unvisited_color
                colors_glow[i] = unvisited_glow
        
        # Update markers with new BRIGHT colors - explicitly set size too for visibility
        self.waypoint_markers.setData(pos=waypoints, color=colors, size=14)
        self.waypoint_markers_glow.setData(pos=waypoints, color=colors_glow, size=22)
    
    def update_waypoint_labels(self):
        """Update waypoint text labels - ensuring they are always visible"""
        # Remove old text items
        for text_item in self.waypoint_text_items:
            self.plot_widget.removeItem(text_item)
        self.waypoint_text_items.clear()
        
        if self.current_trajectory is None:
            return
        
        waypoints = self.current_trajectory['waypoints']
        
        # Create text label for each waypoint with high contrast colors
        for i, wp in enumerate(waypoints):
            # Determine color based on visited status and theme
            # Use VERY HIGH contrast colors for maximum visibility
            if i in self.visited_waypoints:
                # Bright green for visited - highly visible
                if self.current_theme == 'white':
                    color = (0.0, 0.8, 0.0, 1.0)  # Dark green on white
                else:
                    color = (0.3, 1.0, 0.3, 1.0)  # Bright green on black
            else:
                # Maximum contrast for unvisited waypoints
                if self.current_theme == 'white':
                    color = (0.0, 0.0, 0.0, 1.0)  # Pure black on white background
                else:
                    color = (1.0, 1.0, 1.0, 1.0)  # Pure white on black background
            
            # Create text item with waypoint number - LARGE and BOLD for visibility
            # Position offset slightly higher for better visibility
            text = gl.GLTextItem(
                pos=(wp[0], wp[1], wp[2] + 3.0),  # Position higher above waypoint
                text=f"WP{i + 1}",  # Clear "WP" prefix with number
                color=color,
                font=pg.QtGui.QFont('Arial', 16, pg.QtGui.QFont.Bold)  # Larger font
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
        
        # Update waypoint markers with colors - ALWAYS call this to ensure colors are correct
        self.update_waypoint_colors()
        
        # Update waypoint text labels - ALWAYS show WP numbers
        self.update_waypoint_labels()
        
        # Update waypoint connections
        waypoints = self.current_trajectory['waypoints']
        if len(waypoints) > 1:
            # Only show connections if checkbox is enabled
            if self.show_connections:
                self.waypoint_connections.setData(pos=waypoints)
            else:
                self.waypoint_connections.setData(pos=np.array([[0, 0, 0]]))
    
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
