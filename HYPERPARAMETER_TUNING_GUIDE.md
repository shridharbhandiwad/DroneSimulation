# Hyperparameter Tuning Guide
## Optimizing the Drone Trajectory Prediction System

**Document Version:** 1.0  
**Last Updated:** 2025-11-30

---

## Table of Contents

1. [Overview](#1-overview)
2. [Physics Parameters](#2-physics-parameters)
3. [ML Model Architecture](#3-ml-model-architecture)
4. [Training Parameters](#4-training-parameters)
5. [Data Generation](#5-data-generation)
6. [Optimization Strategies](#6-optimization-strategies)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Overview

### 1.1 What to Tune

The system has three main categories of tunable parameters:

1. **Physics Parameters**: Control trajectory generation behavior
2. **ML Model Parameters**: Define neural network architecture
3. **Training Parameters**: Control learning process

### 1.2 Tuning Philosophy

**Priority Order:**
1. Get physics right first (affects all data)
2. Tune model architecture (capacity)
3. Optimize training process (convergence)
4. Fine-tune data generation (augmentation)

**Iterative Process:**
```
Define Baseline → Measure Performance → Adjust Parameters → Evaluate → Repeat
```

---

## 2. Physics Parameters

### 2.1 Speed Parameters

**Location:** `trajectory_generator.py` → `DronePhysics.__init__()`

#### max_speed (default: 15.0 m/s)

**What it affects:**
- Maximum horizontal velocity
- Overall trajectory speed
- Smoothness of turns

**Tuning Guidelines:**

| Value (m/s) | Use Case | Characteristics |
|-------------|----------|-----------------|
| 5-10 | Slow, stable | Very smooth, stable, conservative |
| 10-15 | Moderate (default) | Balanced speed and stability |
| 15-20 | Fast, aggressive | Quick maneuvers, less smooth |
| 20+ | Racing | Very fast, requires tuning other params |

**How to tune:**
```python
# Test different values
for max_speed in [10.0, 12.5, 15.0, 17.5, 20.0]:
    physics = DronePhysics(max_speed=max_speed)
    trajectory = generator.generate(initial_pos, initial_vel, waypoints)
    
    # Evaluate
    avg_speed = np.mean(np.linalg.norm(trajectory['velocities'], axis=1))
    max_accel = np.max(np.linalg.norm(trajectory['accelerations'], axis=1))
    
    print(f"max_speed={max_speed}: avg={avg_speed:.2f}, max_accel={max_accel:.2f}")
```

**Signs you need to adjust:**
- ✗ Drone takes too long to reach waypoints → Increase
- ✗ Overshooting waypoints → Decrease
- ✗ Trajectories look jerky → Decrease

#### max_vertical_speed (default: 5.0 m/s)

**What it affects:**
- Climb/descent rate
- Altitude change smoothness

**Tuning Guidelines:**

| Value (m/s) | Altitude Changes | Smoothness |
|-------------|------------------|------------|
| 2-3 | Very slow | Very smooth |
| 3-5 | Moderate (default) | Smooth |
| 5-8 | Fast | Less smooth |
| 8+ | Very fast | Potential instability |

**Relationship with max_speed:**
```
Recommended: max_vertical_speed = 0.3 * max_speed
```

**Example:**
```python
# For aggressive drone
max_speed = 20.0
max_vertical_speed = 6.0  # 30% of horizontal

# For stable drone
max_speed = 12.0
max_vertical_speed = 4.0
```

### 2.2 Acceleration Parameters

#### max_acceleration (default: 5.0 m/s²)

**What it affects:**
- How quickly drone can change velocity
- Sharpness of turns
- Response time to waypoint changes

**Physical Context:**
- 1 m/s² = 0.1g (very gentle)
- 5 m/s² = 0.5g (moderate)
- 10 m/s² = 1.0g (aggressive)

**Tuning Guidelines:**

| Value (m/s²) | Application | Characteristics |
|--------------|-------------|-----------------|
| 2-3 | Cargo, photography | Very smooth, stable |
| 3-5 | General purpose (default) | Balanced |
| 5-8 | Sport, inspection | Quick response |
| 8+ | Racing, emergency | Very aggressive |

**How to evaluate:**
```python
def evaluate_smoothness(trajectory):
    """Calculate trajectory jerk (derivative of acceleration)"""
    accelerations = trajectory['accelerations']
    dt = trajectory['dt']
    
    # Jerk = da/dt
    jerk = np.diff(accelerations, axis=0) / dt
    jerk_magnitude = np.linalg.norm(jerk, axis=1)
    
    return {
        'avg_jerk': np.mean(jerk_magnitude),
        'max_jerk': np.max(jerk_magnitude),
        'smoothness_score': 1.0 / (1.0 + np.mean(jerk_magnitude))
    }
```

**Target values:**
- avg_jerk < 10 m/s³: Smooth
- avg_jerk 10-20 m/s³: Acceptable
- avg_jerk > 20 m/s³: Too jerky

#### drag_coefficient (default: 0.1)

**What it affects:**
- Deceleration rate when not accelerating
- Energy dissipation
- Coasting behavior

**Physical Interpretation:**
```
F_drag = -drag_coefficient * velocity * |velocity|
```

**Tuning Guidelines:**

| Value | Drone Type | Behavior |
|-------|-----------|----------|
| 0.05-0.08 | Large, streamlined | Long coasting, slow deceleration |
| 0.08-0.12 | Medium (default) | Balanced |
| 0.12-0.20 | Small, high drag | Quick deceleration, short coast |

**Test procedure:**
```python
def test_drag(drag_coefficient):
    """Test coasting distance"""
    physics = DronePhysics(drag_coefficient=drag_coefficient)
    
    # Start with velocity, no thrust
    state = {'position': [0, 0, 5], 'velocity': [10, 0, 0], 'acceleration': [0, 0, 0]}
    
    # Simulate until nearly stopped
    time = 0
    while np.linalg.norm(state['velocity']) > 0.1:
        state = physics.update(state, state['position'], 0.0, dt=0.1)  # No target
        time += 0.1
    
    distance = state['position'][0]
    print(f"drag={drag_coefficient}: coasted {distance:.2f}m in {time:.2f}s")
```

**Expected results:**
- drag=0.05: ~100m, ~10s
- drag=0.10: ~50m, ~5s
- drag=0.20: ~25m, ~2.5s

### 2.3 Control Parameters

#### slowdown_distance (default: 3.0 m)

**What it affects:**
- When drone starts decelerating before waypoint
- Waypoint approach smoothness
- Overshoot prevention

**Tuning Guidelines:**

```
Recommended: slowdown_distance = max_speed²  / (2 * max_acceleration)
```

**Calculation:**
```python
# For max_speed = 15 m/s, max_acceleration = 5 m/s²
# Stopping distance = v² / (2a) = 15² / (2*5) = 22.5m
# Slowdown distance should be less than stopping distance
slowdown_distance = 3.0  # Start slowing at 3m (well before stopping point)
```

**Effect visualization:**
```python
def visualize_slowdown(slowdown_distance):
    distances = np.linspace(0, 10, 100)
    speeds = []
    
    for d in distances:
        if d < slowdown_distance:
            speed = max_speed * (d / slowdown_distance)
        else:
            speed = max_speed
        speeds.append(speed)
    
    plt.plot(distances, speeds)
    plt.xlabel('Distance to Waypoint (m)')
    plt.ylabel('Target Speed (m/s)')
    plt.title(f'Slowdown Distance = {slowdown_distance}m')
```

| Value (m) | Behavior |
|-----------|----------|
| 1-2 | Late braking, possible overshoot |
| 2-4 | Smooth approach (default) |
| 4-6 | Very conservative, slow approach |
| 6+ | Too conservative, inefficient |

#### dt (timestep, default: 0.1 s)

**What it affects:**
- Simulation accuracy
- Computational cost
- Data density for ML

**Tuning Guidelines:**

| Value (s) | Frequency | Use Case | Accuracy |
|-----------|-----------|----------|----------|
| 0.01 | 100 Hz | High precision | Excellent, expensive |
| 0.05 | 20 Hz | Fine control | Good |
| 0.1 | 10 Hz | Standard (default) | Good, efficient |
| 0.2 | 5 Hz | Coarse | Acceptable |
| 0.5+ | ≤2 Hz | Very coarse | Poor |

**Trade-offs:**
- Smaller dt: More accurate, more data points, slower generation
- Larger dt: Less accurate, fewer data points, faster generation

**Choosing dt:**
```python
# Rule of thumb: dt should be small enough that acceleration changes are smooth
max_velocity_change_per_step = max_acceleration * dt
# Should be < 10% of max_speed
recommended_dt = 0.1 * max_speed / max_acceleration
print(f"Recommended dt: {recommended_dt:.3f}s")

# For max_speed=15, max_accel=5: dt <= 0.3s
# Default 0.1s is well within safe range
```

---

## 3. ML Model Architecture

### 3.1 LSTM Dimensions

#### hidden_size (default: 128)

**What it affects:**
- Model capacity (ability to learn complex patterns)
- Training time
- Inference speed
- Memory usage

**Tuning Guidelines:**

| Value | Parameters | Use Case | Performance |
|-------|-----------|----------|-------------|
| 32 | ~30K | Very simple patterns | Fast, may underfit |
| 64 | ~120K | Simple to moderate | Balanced, small models |
| 128 | ~480K | Moderate complexity (default) | Good balance |
| 256 | ~1.9M | Complex patterns | Slower, may overfit |
| 512 | ~7.5M | Very complex | Very slow, often overfits |

**Parameter count formula:**
```
LSTM params ≈ 4 * (input_size * hidden_size + hidden_size²) * num_layers
FC params = hidden_size * 64 + 64 * output_size

For hidden_size=128:
  LSTM: 4 * (13*128 + 128²) * 2 ≈ 144K
  FC: 128*64 + 64*6 ≈ 8.5K
  Total: ~152K parameters
```

**How to choose:**
```python
def estimate_hidden_size(dataset_size, sequence_length, input_size):
    """Estimate appropriate hidden size based on data"""
    # Rule of thumb: params should be < 10% of training samples
    max_params = dataset_size * 0.1
    
    # Solve for hidden_size
    # Simplified: 4 * h² * 2 < max_params
    hidden_size = int(np.sqrt(max_params / 8))
    
    # Round to nearest power of 2
    hidden_size = 2 ** int(np.log2(hidden_size))
    
    return max(32, min(hidden_size, 512))

# Example: 100K samples → ~353 hidden → round to 256
```

**Evaluation:**
```python
# Train with different hidden sizes
for hidden_size in [64, 128, 256]:
    model = DroneTrajectoryLSTM(hidden_size=hidden_size)
    train_loss, val_loss, train_time = train(model, ...)
    
    print(f"hidden_size={hidden_size}")
    print(f"  Train loss: {train_loss:.4f}")
    print(f"  Val loss: {val_loss:.4f}")
    print(f"  Overfitting: {val_loss - train_loss:.4f}")
    print(f"  Train time: {train_time:.1f}s")
```

**Decision criteria:**
- val_loss - train_loss < 0.01: Increase hidden_size (underfitting)
- val_loss - train_loss > 0.05: Decrease hidden_size (overfitting)
- val_loss - train_loss ≈ 0.02: Good balance

#### num_layers (default: 2)

**What it affects:**
- Model depth (hierarchical feature learning)
- Training difficulty
- Risk of overfitting

**Tuning Guidelines:**

| Layers | Characteristics | Use Case |
|--------|----------------|----------|
| 1 | Simple, fast training | Simple patterns, small datasets |
| 2 | Standard (default) | Most applications |
| 3 | Deep, complex | Complex temporal patterns |
| 4+ | Very deep | Rarely needed, hard to train |

**Layer capacity trade-off:**
```python
# Same capacity, different architectures:
# Option 1: Wide and shallow
model_a = LSTM(hidden_size=256, num_layers=1)  # ~500K params

# Option 2: Narrow and deep (default)
model_b = LSTM(hidden_size=128, num_layers=2)  # ~150K params

# Option 3: Deep and narrow
model_c = LSTM(hidden_size=64, num_layers=3)   # ~80K params
```

**General guidance:**
- 1 layer: Linear/simple patterns only
- 2 layers: Captures most temporal dependencies (recommended)
- 3+ layers: Diminishing returns, harder to train

#### sequence_length (default: 10)

**What it affects:**
- How much history the model sees
- Long-term dependency learning
- Input size and memory usage

**Tuning Guidelines:**

| Length | Time Window | Use Case | Memory |
|--------|------------|----------|---------|
| 5 | 0.5s | Short-term only | Low |
| 10 | 1.0s (default) | Standard prediction | Medium |
| 20 | 2.0s | Long-term patterns | High |
| 50 | 5.0s | Very long-term | Very high |

**How to choose:**
```python
# Analyze trajectory autocorrelation
def analyze_temporal_dependence(trajectory):
    positions = trajectory['positions']
    
    # Calculate autocorrelation
    autocorr = []
    for lag in range(1, 50):
        corr = np.corrcoef(positions[:-lag].flatten(), 
                           positions[lag:].flatten())[0, 1]
        autocorr.append(corr)
    
    # Find where correlation drops below threshold
    threshold = 0.7
    effective_length = np.argmax(np.array(autocorr) < threshold)
    
    return effective_length

# If effective_length = 8, use sequence_length = 10 (with margin)
```

**Trade-offs:**
- Shorter: Faster training, less context, may miss patterns
- Longer: Slower training, more context, may overfit

### 3.2 Regularization

#### dropout (default: 0.2)

**What it affects:**
- Overfitting prevention
- Model robustness
- Training stability

**Tuning Guidelines:**

| Value | Effect | Use Case |
|-------|--------|----------|
| 0.0 | No regularization | Small datasets, underfitting |
| 0.1 | Light regularization | Large datasets |
| 0.2 | Moderate (default) | Standard |
| 0.3 | Strong regularization | Overfitting problems |
| 0.5+ | Very strong | Rarely needed, may underfit |

**How to tune:**
```python
# Grid search
for dropout in [0.0, 0.1, 0.2, 0.3]:
    model = DroneTrajectoryLSTM(dropout=dropout)
    train_loss, val_loss = train(model, ...)
    
    overfitting = val_loss - train_loss
    print(f"dropout={dropout}: overfitting={overfitting:.4f}")

# Choose dropout where overfitting is minimized
```

**Signs of improper dropout:**
- val_loss >> train_loss: Increase dropout
- val_loss ≈ train_loss (both high): Decrease dropout

---

## 4. Training Parameters

### 4.1 Learning Rate

#### learning_rate (default: 0.001)

**What it affects:**
- Training speed
- Convergence quality
- Stability

**Tuning Guidelines:**

| Value | Behavior | Use Case |
|-------|----------|----------|
| 0.0001 | Very slow, stable | Fine-tuning, nearly converged |
| 0.0005 | Slow, stable | Conservative |
| 0.001 | Standard (default) | Most cases |
| 0.003 | Fast, less stable | Initial exploration |
| 0.01+ | Very fast, unstable | Rarely useful |

**Learning rate schedule (default):**
```python
scheduler = ReduceLROnPlateau(
    optimizer,
    mode='min',
    factor=0.5,       # Multiply LR by 0.5
    patience=5,       # Wait 5 epochs without improvement
    min_lr=1e-6       # Don't go below this
)
```

**How it works:**
```
Epoch 1-10: LR = 0.001 (loss decreasing)
Epoch 11-15: LR = 0.001 (loss plateaus)
Epoch 16: LR = 0.0005 (reduced)
Epoch 17-25: LR = 0.0005 (loss decreasing)
Epoch 26-30: LR = 0.0005 (loss plateaus)
Epoch 31: LR = 0.00025 (reduced)
...
```

**Finding optimal LR:**
```python
def lr_range_test(model, train_loader, min_lr=1e-6, max_lr=1.0, num_iterations=100):
    """Find optimal learning rate"""
    lrs = np.logspace(np.log10(min_lr), np.log10(max_lr), num_iterations)
    losses = []
    
    for lr in lrs:
        optimizer = Adam(model.parameters(), lr=lr)
        loss = train_one_batch(model, train_loader, optimizer)
        losses.append(loss)
    
    # Plot
    plt.semilogx(lrs, losses)
    plt.xlabel('Learning Rate')
    plt.ylabel('Loss')
    
    # Optimal: Steepest descent point
    optimal_lr = lrs[np.argmin(np.gradient(losses))]
    return optimal_lr
```

### 4.2 Batch Size

#### batch_size (default: 64)

**What it affects:**
- Training stability
- Gradient quality
- Memory usage
- Training speed

**Tuning Guidelines:**

| Value | Characteristics | Use Case |
|-------|----------------|----------|
| 16 | Noisy gradients, less memory | Small GPUs |
| 32 | Moderate noise | Standard small models |
| 64 | Balanced (default) | Most cases |
| 128 | Stable gradients | Large datasets, big GPUs |
| 256+ | Very stable, high memory | Distributed training |

**Trade-offs:**
```
Small batch (16):
  ✓ Less memory
  ✓ More updates per epoch
  ✗ Noisy gradients
  ✗ Slower per-batch (less GPU utilization)

Large batch (256):
  ✓ Stable gradients
  ✓ Faster per-batch (full GPU)
  ✗ More memory
  ✗ Fewer updates per epoch
```

**How to choose:**
```python
# Find largest batch size that fits in memory
for batch_size in [32, 64, 128, 256]:
    try:
        model = DroneTrajectoryLSTM()
        train_loader = DataLoader(dataset, batch_size=batch_size)
        
        # Try one epoch
        train_epoch(model, train_loader, ...)
        print(f"batch_size={batch_size}: OK")
    except RuntimeError as e:
        if "out of memory" in str(e):
            print(f"batch_size={batch_size}: OOM")
            break
```

**Rule of thumb:**
- Use largest batch size that fits in memory
- If training is noisy: increase batch size
- If convergence is slow: decrease batch size (more updates)

### 4.3 Number of Epochs

#### num_epochs (default: 50)

**What it affects:**
- Training duration
- Model performance
- Risk of overfitting

**Tuning Guidelines:**

| Epochs | Use Case |
|--------|----------|
| 10-20 | Quick prototyping |
| 30-50 | Standard (default) |
| 50-100 | Large datasets, complex models |
| 100+ | Rarely needed (usually overfits) |

**Early stopping:**
```python
class EarlyStopping:
    def __init__(self, patience=10, min_delta=0.001):
        self.patience = patience
        self.min_delta = min_delta
        self.best_loss = float('inf')
        self.counter = 0
    
    def __call__(self, val_loss):
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            return False  # Continue training
        else:
            self.counter += 1
            return self.counter >= self.patience  # Stop if patience exceeded
```

**Usage:**
```python
early_stopping = EarlyStopping(patience=10)

for epoch in range(num_epochs):
    train_loss = train_epoch(...)
    val_loss = validate(...)
    
    if early_stopping(val_loss):
        print(f"Early stopping at epoch {epoch}")
        break
```

---

## 5. Data Generation

### 5.1 Dataset Size

#### num_trajectories (default: 1000)

**What it affects:**
- Model performance
- Training time
- Overfitting risk

**Tuning Guidelines:**

| Trajectories | Samples (~) | Use Case | Training Time |
|--------------|------------|----------|---------------|
| 100 | 10K | Quick prototyping | ~1 minute |
| 500 | 50K | Small-scale | ~5 minutes |
| 1000 | 100K | Standard (default) | ~10 minutes |
| 5000 | 500K | Large-scale | ~50 minutes |
| 10000+ | 1M+ | Production | Hours |

**How much data do you need?**
```python
# Rule of thumb: 10-100 samples per parameter
num_params = count_parameters(model)  # e.g., 150K

min_samples = num_params * 10        # 1.5M (conservative)
recommended_samples = num_params * 50 # 7.5M (ideal)
max_samples = num_params * 100       # 15M (overkill)

# Convert to trajectories
samples_per_trajectory = 100  # Average
num_trajectories = recommended_samples / samples_per_trajectory
print(f"Recommended trajectories: {num_trajectories:.0f}")
```

### 5.2 Noise Augmentation

#### position_noise, velocity_noise (defaults: 0.1, 0.05)

**What it affects:**
- Model robustness to sensor noise
- Generalization ability
- Training data diversity

**Tuning Guidelines:**

**Position noise (meters):**

| Value (m) | Interpretation | Use Case |
|-----------|---------------|----------|
| 0.0 | Perfect sensors | Ideal conditions |
| 0.05 | High-end GPS | Professional drones |
| 0.1 | Consumer GPS (default) | Standard drones |
| 0.5 | Poor GPS | Low-cost systems |
| 1.0+ | Very poor | Not recommended |

**Velocity noise (m/s):**

| Value (m/s) | Interpretation | Use Case |
|-------------|---------------|----------|
| 0.0 | Perfect IMU | Ideal conditions |
| 0.05 | High-end IMU (default) | Standard |
| 0.1 | Consumer IMU | Budget drones |
| 0.2+ | Poor IMU | Not recommended |

**Noise application:**
```python
# 30% of trajectories get noise (default)
noise_probability = 0.3

for i in range(num_trajectories):
    trajectory = generate_trajectory(...)
    
    if random.random() < noise_probability:
        trajectory = add_noise(
            trajectory,
            position_noise=0.1,  # ±10cm
            velocity_noise=0.05  # ±5cm/s
        )
```

**How to tune:**
```python
# Match noise to your hardware
gps_accuracy = 0.15  # meters (from spec sheet)
imu_accuracy = 0.08  # m/s (from spec sheet)

position_noise = gps_accuracy * 0.67  # Use 2/3 of max error
velocity_noise = imu_accuracy * 0.67

# Or, tune empirically
for pos_noise in [0.05, 0.1, 0.2]:
    model = train_with_noise(position_noise=pos_noise, ...)
    real_world_error = test_on_real_drone(model)
    print(f"Training noise={pos_noise}: Real error={real_world_error}")
```

---

## 6. Optimization Strategies

### 6.1 Systematic Tuning Process

**Step 1: Baseline**
```python
# Default configuration
baseline_config = {
    'max_speed': 15.0,
    'max_acceleration': 5.0,
    'hidden_size': 128,
    'num_layers': 2,
    'learning_rate': 0.001,
    'batch_size': 64,
    'num_epochs': 50
}

baseline_loss = train_and_evaluate(baseline_config)
print(f"Baseline validation loss: {baseline_loss:.4f}")
```

**Step 2: One-at-a-Time (OAT) Tuning**
```python
def tune_parameter(param_name, values, baseline_config):
    results = []
    
    for value in values:
        config = baseline_config.copy()
        config[param_name] = value
        
        loss = train_and_evaluate(config)
        results.append((value, loss))
        print(f"{param_name}={value}: loss={loss:.4f}")
    
    # Find best
    best_value, best_loss = min(results, key=lambda x: x[1])
    return best_value, best_loss

# Tune each parameter
best_max_speed = tune_parameter('max_speed', [10, 12.5, 15, 17.5], baseline_config)
best_hidden_size = tune_parameter('hidden_size', [64, 128, 256], baseline_config)
# ...
```

**Step 3: Grid Search (Key Parameters)**
```python
from itertools import product

param_grid = {
    'learning_rate': [0.0005, 0.001, 0.002],
    'batch_size': [32, 64, 128],
    'hidden_size': [64, 128, 256]
}

best_config = None
best_loss = float('inf')

for lr, bs, hs in product(*param_grid.values()):
    config = {'learning_rate': lr, 'batch_size': bs, 'hidden_size': hs}
    loss = train_and_evaluate(config)
    
    if loss < best_loss:
        best_loss = loss
        best_config = config

print(f"Best config: {best_config}")
print(f"Best loss: {best_loss:.4f}")
```

**Step 4: Random Search (Exploration)**
```python
import random

def random_search(num_trials=20):
    param_ranges = {
        'max_speed': (10.0, 20.0),
        'learning_rate': (0.0001, 0.01),
        'hidden_size': [64, 128, 256, 512],
        'dropout': (0.0, 0.4)
    }
    
    results = []
    for _ in range(num_trials):
        config = {
            'max_speed': random.uniform(*param_ranges['max_speed']),
            'learning_rate': random.uniform(*param_ranges['learning_rate']),
            'hidden_size': random.choice(param_ranges['hidden_size']),
            'dropout': random.uniform(*param_ranges['dropout'])
        }
        
        loss = train_and_evaluate(config)
        results.append((config, loss))
    
    return sorted(results, key=lambda x: x[1])[:5]  # Top 5
```

### 6.2 Performance Metrics

**Evaluation Framework:**
```python
def comprehensive_evaluation(model, test_loader):
    """Evaluate model performance"""
    metrics = {
        'position_mae': [],
        'position_rmse': [],
        'velocity_mae': [],
        'velocity_rmse': [],
        'direction_error': []
    }
    
    for inputs, targets in test_loader:
        predictions = model(inputs)
        
        # Position errors
        pos_error = torch.abs(predictions[:, :3] - targets[:, :3])
        metrics['position_mae'].extend(pos_error.mean(dim=1).tolist())
        metrics['position_rmse'].extend(torch.sqrt((pos_error**2).mean(dim=1)).tolist())
        
        # Velocity errors
        vel_error = torch.abs(predictions[:, 3:6] - targets[:, 3:6])
        metrics['velocity_mae'].extend(vel_error.mean(dim=1).tolist())
        metrics['velocity_rmse'].extend(torch.sqrt((vel_error**2).mean(dim=1)).tolist())
        
        # Direction error (angle between predicted and true velocity)
        pred_vel = predictions[:, 3:6]
        true_vel = targets[:, 3:6]
        dot_product = (pred_vel * true_vel).sum(dim=1)
        pred_norm = pred_vel.norm(dim=1)
        true_norm = true_vel.norm(dim=1)
        cos_angle = dot_product / (pred_norm * true_norm + 1e-6)
        angle_error = torch.acos(torch.clamp(cos_angle, -1, 1))
        metrics['direction_error'].extend(angle_error.tolist())
    
    # Aggregate
    summary = {
        'position_mae': np.mean(metrics['position_mae']),
        'position_rmse': np.mean(metrics['position_rmse']),
        'velocity_mae': np.mean(metrics['velocity_mae']),
        'velocity_rmse': np.mean(metrics['velocity_rmse']),
        'direction_error_deg': np.degrees(np.mean(metrics['direction_error']))
    }
    
    return summary
```

**Target Performance:**
```
Excellent:
  position_mae < 0.2m
  position_rmse < 0.3m
  velocity_mae < 0.1 m/s
  direction_error < 2°

Good:
  position_mae < 0.4m
  position_rmse < 0.6m
  velocity_mae < 0.2 m/s
  direction_error < 5°

Acceptable:
  position_mae < 0.8m
  position_rmse < 1.0m
  velocity_mae < 0.4 m/s
  direction_error < 10°
```

---

## 7. Troubleshooting

### 7.1 Common Issues

#### Issue: High training loss, not decreasing

**Possible causes:**
1. Learning rate too low
2. Model too small (underfitting)
3. Bad initialization

**Solutions:**
```python
# 1. Increase learning rate
learning_rate = 0.003  # From 0.001

# 2. Increase model capacity
hidden_size = 256      # From 128
num_layers = 3         # From 2

# 3. Check initialization
print(f"Initial loss: {initial_loss:.4f}")
# Should be around 2-5 for MSE. If much higher, initialization problem.
```

#### Issue: Train loss low, validation loss high (overfitting)

**Solutions:**
```python
# 1. Increase dropout
dropout = 0.3          # From 0.2

# 2. Reduce model size
hidden_size = 64       # From 128

# 3. Generate more data
num_trajectories = 2000  # From 1000

# 4. Add more noise augmentation
noise_probability = 0.5  # From 0.3
position_noise = 0.15    # From 0.1
```

#### Issue: Loss oscillating, not converging

**Solutions:**
```python
# 1. Reduce learning rate
learning_rate = 0.0005  # From 0.001

# 2. Increase batch size
batch_size = 128        # From 64

# 3. Add gradient clipping
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

#### Issue: Model predicts NaN

**Possible causes:**
1. Learning rate too high
2. Exploding gradients
3. Bad normalization

**Solutions:**
```python
# 1. Reduce learning rate
learning_rate = 0.0001

# 2. Add gradient clipping
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=0.5)

# 3. Check normalization
print(f"pos_std: {pos_std}")  # Should not be zero
print(f"vel_std: {vel_std}")  # Should not be zero

# 4. Add epsilon to prevent division by zero
normalized = (value - mean) / (std + 1e-6)
```

### 7.2 Diagnostic Tools

**Learning Curve Analysis:**
```python
def plot_learning_curves(train_losses, val_losses):
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    
    # Diagnose
    final_gap = val_losses[-1] - train_losses[-1]
    if final_gap > 0.1:
        plt.title('OVERFITTING: Increase regularization')
    elif train_losses[-1] > 1.0:
        plt.title('UNDERFITTING: Increase capacity or train longer')
    else:
        plt.title('GOOD FIT')
    
    plt.show()
```

**Prediction Visualization:**
```python
def visualize_predictions(model, test_trajectory):
    """Visualize model predictions vs ground truth"""
    predictions = []
    ground_truth = test_trajectory['positions']
    
    # Make predictions
    for i in range(10, len(ground_truth)):
        history = test_trajectory['positions'][i-10:i]
        pred = model.predict(history, test_trajectory['waypoints'][0])
        predictions.append(pred['position'])
    
    predictions = np.array(predictions)
    
    # Plot
    fig = plt.figure(figsize=(12, 4))
    
    for dim, label in enumerate(['X', 'Y', 'Z']):
        plt.subplot(1, 3, dim+1)
        plt.plot(ground_truth[10:, dim], label='Ground Truth')
        plt.plot(predictions[:, dim], label='Prediction')
        plt.xlabel('Timestep')
        plt.ylabel(f'{label} Position (m)')
        plt.legend()
        plt.grid(True)
    
    plt.tight_layout()
    plt.show()
```

---

## Summary: Quick Reference

### Recommended Starting Points

**For General Use:**
```python
physics_params = {
    'max_speed': 15.0,
    'max_acceleration': 5.0,
    'max_vertical_speed': 5.0,
    'drag_coefficient': 0.1,
    'dt': 0.1
}

model_params = {
    'hidden_size': 128,
    'num_layers': 2,
    'dropout': 0.2,
    'sequence_length': 10
}

training_params = {
    'learning_rate': 0.001,
    'batch_size': 64,
    'num_epochs': 50
}

data_params = {
    'num_trajectories': 1000,
    'position_noise': 0.1,
    'velocity_noise': 0.05,
    'noise_probability': 0.3
}
```

**For Fast/Aggressive Drones:**
```python
physics_params = {
    'max_speed': 20.0,          # Increased
    'max_acceleration': 8.0,    # Increased
    'max_vertical_speed': 6.0   # Increased
}
```

**For Slow/Stable Drones:**
```python
physics_params = {
    'max_speed': 10.0,          # Decreased
    'max_acceleration': 3.0,    # Decreased
    'max_vertical_speed': 3.0   # Decreased
}
```

---

**End of Hyperparameter Tuning Guide**
