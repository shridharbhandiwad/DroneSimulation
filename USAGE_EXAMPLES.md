# Usage Examples

Comprehensive examples for using the Drone Trajectory System in various scenarios.

## Table of Contents

1. [Python Examples](#python-examples)
2. [C++ Examples](#cpp-examples)
3. [Integration Examples](#integration-examples)
4. [Advanced Usage](#advanced-usage)

---

## Python Examples

### Example 1: Basic Trajectory Generation

```python
from trajectory_generator import TrajectoryGenerator
import numpy as np

# Create generator
generator = TrajectoryGenerator(dt=0.1)  # 100ms timestep

# Define flight parameters
initial_position = np.array([0, 0, 5])  # Start at (0,0,5)
initial_velocity = np.array([0, 0, 0])  # Start from rest

waypoints = [
    np.array([10, 10, 8]),    # Waypoint 1
    np.array([20, 5, 10]),    # Waypoint 2
    np.array([15, -10, 7]),   # Waypoint 3
    np.array([0, 0, 5])       # Return home
]

# Generate trajectory
trajectory = generator.generate(
    initial_position,
    initial_velocity,
    waypoints,
    max_time=60.0  # 60 second simulation
)

# Access results
positions = trajectory['positions']     # Nx3 array
velocities = trajectory['velocities']   # Nx3 array
times = trajectory['times']             # N array

print(f"Generated {len(positions)} steps")
print(f"Duration: {times[-1]:.1f} seconds")
```

### Example 2: Using ML Predictor

```python
from ml_model import TrajectoryPredictor
import numpy as np

# Load trained model
predictor = TrajectoryPredictor(model_path='models/best_model.pth')

# Build state history
history = []
for i in range(10):  # Need 10 timesteps
    state = {
        'position': np.array([i*1.0, i*1.0, 5.0]),
        'velocity': np.array([1.0, 1.0, 0.0]),
        'acceleration': np.array([0.0, 0.0, 0.0])
    }
    history.append(state)

# Predict next state
target_waypoint = np.array([15.0, 15.0, 8.0])
prediction = predictor.predict(history, target_waypoint)

print("Predicted position:", prediction['position'])
print("Predicted velocity:", prediction['velocity'])
```

### Example 3: Custom Waypoint Path

```python
from trajectory_generator import TrajectoryGenerator
import numpy as np

def circular_path(center, radius, height, num_points=8):
    """Generate waypoints in a circle"""
    angles = np.linspace(0, 2*np.pi, num_points, endpoint=False)
    waypoints = []
    for angle in angles:
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        waypoints.append(np.array([x, y, height]))
    return waypoints

def spiral_path(center, max_radius, start_height, end_height, num_points=20):
    """Generate waypoints in a spiral"""
    waypoints = []
    for i in range(num_points):
        t = i / (num_points - 1)
        radius = max_radius * t
        angle = 4 * np.pi * t  # 2 full rotations
        height = start_height + (end_height - start_height) * t
        
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        waypoints.append(np.array([x, y, height]))
    return waypoints

# Generate circular path
circular = circular_path(center=[0, 0], radius=20, height=10, num_points=12)

# Generate spiral path
spiral = spiral_path(center=[0, 0], max_radius=25, 
                     start_height=5, end_height=15, num_points=30)

# Use with trajectory generator
generator = TrajectoryGenerator()
traj_circular = generator.generate(np.array([0, 0, 5]), 
                                    np.array([0, 0, 0]), 
                                    circular)
traj_spiral = generator.generate(np.array([0, 0, 5]),
                                  np.array([0, 0, 0]),
                                  spiral)
```

### Example 4: Real-Time Simulation Loop

```python
from trajectory_generator import TrajectoryGenerator
from ml_model import TrajectoryPredictor
import numpy as np
import time

# Setup
generator = TrajectoryGenerator(dt=0.1)
predictor = TrajectoryPredictor('models/best_model.pth')

# Initial state
current_state = {
    'position': np.array([0.0, 0.0, 5.0]),
    'velocity': np.array([0.0, 0.0, 0.0]),
    'acceleration': np.array([0.0, 0.0, 0.0]),
    'time': 0.0
}

# Waypoints
waypoints = [np.array([10, 10, 8]), np.array([20, 5, 10])]
current_wp_idx = 0

# History buffer
history = []

# Simulation loop
while current_wp_idx < len(waypoints):
    # Add current state to history
    history.append(current_state.copy())
    if len(history) > 10:
        history.pop(0)
    
    # Get target
    target = waypoints[current_wp_idx]
    
    # Predict next state
    if len(history) >= 10 and predictor:
        prediction = predictor.predict(history, target)
        next_pos = prediction['position']
        next_vel = prediction['velocity']
    else:
        # Use physics fallback
        physics = generator.physics
        next_state_dict = physics.update(current_state, target, 0.1)
        next_pos = next_state_dict['position']
        next_vel = next_state_dict['velocity']
    
    # Update state
    current_state['position'] = next_pos
    current_state['velocity'] = next_vel
    current_state['time'] += 0.1
    
    # Check waypoint reached
    dist = np.linalg.norm(target - next_pos)
    if dist < 0.5:
        current_wp_idx += 1
        print(f"Reached waypoint {current_wp_idx}")
    
    # Print status
    if int(current_state['time'] * 10) % 10 == 0:  # Every second
        print(f"t={current_state['time']:.1f}s: "
              f"pos=({next_pos[0]:.1f}, {next_pos[1]:.1f}, {next_pos[2]:.1f}), "
              f"dist={dist:.1f}m")
    
    # Real-time delay
    time.sleep(0.1)

print("Mission complete!")
```

### Example 5: Batch Prediction and Analysis

```python
from trajectory_generator import TrajectoryGenerator
import numpy as np
import matplotlib.pyplot as plt

def analyze_trajectory(trajectory):
    """Analyze trajectory metrics"""
    positions = trajectory['positions']
    velocities = trajectory['velocities']
    accelerations = trajectory['accelerations']
    times = trajectory['times']
    
    # Calculate metrics
    speeds = np.linalg.norm(velocities, axis=1)
    accels = np.linalg.norm(accelerations, axis=1)
    
    # Total distance
    segments = np.diff(positions, axis=0)
    distances = np.linalg.norm(segments, axis=1)
    total_distance = np.sum(distances)
    
    # Statistics
    metrics = {
        'duration': times[-1],
        'total_distance': total_distance,
        'max_speed': np.max(speeds),
        'avg_speed': np.mean(speeds),
        'max_acceleration': np.max(accels),
        'avg_acceleration': np.mean(accels)
    }
    
    return metrics

# Generate multiple trajectories
generator = TrajectoryGenerator()
trajectories = []
metrics_list = []

for i in range(10):
    # Random waypoints
    num_wp = np.random.randint(3, 7)
    waypoints = [
        np.random.uniform(-20, 20, 3) for _ in range(num_wp)
    ]
    
    traj = generator.generate(
        np.array([0, 0, 5]),
        np.array([0, 0, 0]),
        waypoints
    )
    
    trajectories.append(traj)
    metrics = analyze_trajectory(traj)
    metrics_list.append(metrics)
    
    print(f"Trajectory {i+1}: {metrics}")

# Plot statistics
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

axes[0, 0].hist([m['duration'] for m in metrics_list], bins=10)
axes[0, 0].set_title('Duration Distribution')
axes[0, 0].set_xlabel('Time (s)')

axes[0, 1].hist([m['total_distance'] for m in metrics_list], bins=10)
axes[0, 1].set_title('Distance Distribution')
axes[0, 1].set_xlabel('Distance (m)')

axes[1, 0].hist([m['max_speed'] for m in metrics_list], bins=10)
axes[1, 0].set_title('Max Speed Distribution')
axes[1, 0].set_xlabel('Speed (m/s)')

axes[1, 1].hist([m['max_acceleration'] for m in metrics_list], bins=10)
axes[1, 1].set_title('Max Acceleration Distribution')
axes[1, 1].set_xlabel('Acceleration (m/s²)')

plt.tight_layout()
plt.savefig('trajectory_analysis.png')
```

---

## C++ Examples

### Example 1: Basic C++ Prediction

```cpp
#include "drone_trajectory.h"
#include <iostream>

int main() {
    using namespace drone;
    
    // Create predictor
    TrajectoryPredictor predictor(
        "models/drone_trajectory.onnx",
        "models/drone_trajectory_normalization.txt",
        10  // sequence length
    );
    
    // Initialize
    if (!predictor.initialize()) {
        std::cerr << "Failed to initialize" << std::endl;
        return 1;
    }
    
    // Build history
    for (int i = 0; i < 10; i++) {
        DroneState state;
        state.position = Vec3(i * 1.0f, i * 1.0f, 5.0f);
        state.velocity = Vec3(1.0f, 1.0f, 0.0f);
        state.acceleration = Vec3(0.0f, 0.0f, 0.0f);
        state.timestamp = i * 0.1;
        predictor.addState(state);
    }
    
    // Predict
    Vec3 target(15.0f, 15.0f, 8.0f);
    DroneState predicted;
    
    if (predictor.predict(target, predicted)) {
        std::cout << "Predicted position: ("
                  << predicted.position.x << ", "
                  << predicted.position.y << ", "
                  << predicted.position.z << ")" << std::endl;
    }
    
    return 0;
}
```

### Example 2: Real-Time Loop in C++

```cpp
#include "drone_trajectory.h"
#include <iostream>
#include <vector>
#include <chrono>
#include <thread>

int main() {
    using namespace drone;
    
    // Setup
    TrajectoryPredictor predictor(
        "models/drone_trajectory.onnx",
        "models/drone_trajectory_normalization.txt"
    );
    predictor.initialize();
    
    // Current state
    DroneState current;
    current.position = Vec3(0, 0, 5);
    current.velocity = Vec3(0, 0, 0);
    current.acceleration = Vec3(0, 0, 0);
    current.timestamp = 0.0;
    
    // Waypoints
    std::vector<Vec3> waypoints = {
        Vec3(10, 10, 8),
        Vec3(20, 5, 10)
    };
    size_t current_wp = 0;
    
    // Build initial history
    PhysicsTrajectoryGenerator physics;
    for (int i = 0; i < 10; i++) {
        predictor.addState(current);
        DroneState next;
        physics.update(current, waypoints[current_wp], 0.1f, next);
        current = next;
    }
    
    // Real-time loop
    while (current_wp < waypoints.size()) {
        Vec3 target = waypoints[current_wp];
        
        // Predict
        DroneState predicted;
        if (predictor.predict(target, predicted)) {
            current = predicted;
            predictor.addState(current);
            
            // Check if reached
            float dist = (target - current.position).norm();
            if (dist < 0.5f) {
                current_wp++;
                std::cout << "Reached waypoint " << current_wp << std::endl;
            }
            
            // Status
            std::cout << "t=" << current.timestamp
                     << "s, pos=(" << current.position.x
                     << "," << current.position.y
                     << "," << current.position.z
                     << "), dist=" << dist << "m" << std::endl;
        }
        
        // Wait 100ms
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    return 0;
}
```

### Example 3: Thread-Safe Predictor Wrapper

```cpp
#include "drone_trajectory.h"
#include <mutex>
#include <memory>

class ThreadSafePredictor {
public:
    ThreadSafePredictor(const std::string& model_path,
                       const std::string& norm_path)
        : predictor_(std::make_unique<drone::TrajectoryPredictor>(
            model_path, norm_path)) {
        predictor_->initialize();
    }
    
    void addState(const drone::DroneState& state) {
        std::lock_guard<std::mutex> lock(mutex_);
        predictor_->addState(state);
    }
    
    bool predict(const drone::Vec3& target, drone::DroneState& predicted) {
        std::lock_guard<std::mutex> lock(mutex_);
        return predictor_->predict(target, predicted);
    }
    
    void reset() {
        std::lock_guard<std::mutex> lock(mutex_);
        predictor_->reset();
    }
    
private:
    std::unique_ptr<drone::TrajectoryPredictor> predictor_;
    std::mutex mutex_;
};

// Usage in multi-threaded application
ThreadSafePredictor predictor("model.onnx", "norm.txt");

// Thread 1: Update states
void state_update_thread() {
    while (running) {
        drone::DroneState state = get_current_state();
        predictor.addState(state);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

// Thread 2: Predict
void prediction_thread() {
    while (running) {
        drone::Vec3 target = get_target_waypoint();
        drone::DroneState predicted;
        if (predictor.predict(target, predicted)) {
            publish_prediction(predicted);
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
}
```

---

## Integration Examples

### ROS Integration (Python)

```python
#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import PoseStamped, TwistStamped
from nav_msgs.msg import Path
from ml_model import TrajectoryPredictor
import numpy as np

class DronePredictorNode:
    def __init__(self):
        rospy.init_node('drone_predictor')
        
        # Load model
        self.predictor = TrajectoryPredictor('models/best_model.pth')
        self.history = []
        
        # Subscribers
        rospy.Subscriber('/drone/pose', PoseStamped, self.pose_callback)
        rospy.Subscriber('/drone/velocity', TwistStamped, self.velocity_callback)
        rospy.Subscriber('/drone/target', PoseStamped, self.target_callback)
        
        # Publishers
        self.pred_pub = rospy.Publisher('/drone/predicted_path', 
                                       Path, queue_size=10)
        
        self.current_pose = None
        self.current_velocity = None
        self.target = None
        
    def pose_callback(self, msg):
        self.current_pose = msg
        
    def velocity_callback(self, msg):
        self.current_velocity = msg
        
    def target_callback(self, msg):
        self.target = msg
        self.predict()
    
    def predict(self):
        if len(self.history) < 10:
            return
        
        if self.target is None:
            return
        
        # Extract target
        target = np.array([
            self.target.pose.position.x,
            self.target.pose.position.y,
            self.target.pose.position.z
        ])
        
        # Predict
        prediction = self.predictor.predict(self.history, target)
        
        # Publish
        path = Path()
        path.header.frame_id = "world"
        path.header.stamp = rospy.Time.now()
        
        pose = PoseStamped()
        pose.pose.position.x = prediction['position'][0]
        pose.pose.position.y = prediction['position'][1]
        pose.pose.position.z = prediction['position'][2]
        path.poses.append(pose)
        
        self.pred_pub.publish(path)
    
    def run(self):
        rospy.spin()

if __name__ == '__main__':
    node = DronePredictorNode()
    node.run()
```

### Web API (Flask)

```python
from flask import Flask, request, jsonify
from ml_model import TrajectoryPredictor
import numpy as np

app = Flask(__name__)
predictor = TrajectoryPredictor('models/best_model.pth')

@app.route('/predict', methods=['POST'])
def predict():
    """
    POST /predict
    Body: {
        "history": [[x, y, z, vx, vy, vz, ax, ay, az], ...],
        "target": [x, y, z]
    }
    """
    data = request.json
    
    # Parse history
    history = []
    for state_data in data['history']:
        state = {
            'position': np.array(state_data[0:3]),
            'velocity': np.array(state_data[3:6]),
            'acceleration': np.array(state_data[6:9])
        }
        history.append(state)
    
    # Parse target
    target = np.array(data['target'])
    
    # Predict
    prediction = predictor.predict(history, target)
    
    return jsonify({
        'position': prediction['position'].tolist(),
        'velocity': prediction['velocity'].tolist()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## Advanced Usage

### Custom Loss Function

```python
import torch
import torch.nn as nn

class WeightedMSELoss(nn.Module):
    """Weight position errors more than velocity"""
    def __init__(self, pos_weight=2.0):
        super().__init__()
        self.pos_weight = pos_weight
        
    def forward(self, pred, target):
        # Split position and velocity
        pred_pos = pred[:, :3]
        pred_vel = pred[:, 3:]
        target_pos = target[:, :3]
        target_vel = target[:, 3:]
        
        # Calculate losses
        pos_loss = nn.functional.mse_loss(pred_pos, target_pos)
        vel_loss = nn.functional.mse_loss(pred_vel, target_vel)
        
        return self.pos_weight * pos_loss + vel_loss

# Use in training
criterion = WeightedMSELoss(pos_weight=2.0)
```

### Online Learning

```python
class OnlinePredictor(TrajectoryPredictor):
    """Predictor with online learning capability"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.0001)
        self.criterion = nn.MSELoss()
        
    def update(self, history, target, actual_next):
        """Update model with actual outcome"""
        # Predict
        x = self.prepare_input(history, target)
        self.model.train()
        
        # Forward
        output, _ = self.model(x)
        
        # Calculate loss
        actual_tensor = torch.FloatTensor(
            np.concatenate([actual_next['position'], 
                          actual_next['velocity']])
        ).unsqueeze(0).to(self.device)
        
        loss = self.criterion(output, actual_tensor)
        
        # Backward
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        self.model.eval()
        return loss.item()
```

This comprehensive collection of examples should help you integrate and use the drone trajectory system in various scenarios!
