# Design Decisions
## Architectural Choices and Rationale

**Document Version:** 1.0  
**Last Updated:** 2025-11-30

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Physics Engine](#2-physics-engine)
3. [Machine Learning Model](#3-machine-learning-model)
4. [Implementation Choices](#4-implementation-choices)
5. [User Interface](#5-user-interface)
6. [Trade-offs](#6-trade-offs)

---

## 1. System Architecture

### 1.1 Hybrid Physics-ML Approach

**Decision:** Use physics-based generation for training data and runtime fallback, with ML for enhanced prediction

**Alternatives Considered:**
1. Pure physics-based (no ML)
2. Pure ML-based (data-driven only)
3. Hybrid (chosen)

**Rationale:**

| Approach | Pros | Cons |
|----------|------|------|
| Pure Physics | ✓ No training needed<br>✓ Interpretable<br>✓ Guaranteed stability | ✗ Cannot learn from data<br>✗ Fixed accuracy<br>✗ Hard to tune |
| Pure ML | ✓ Can capture complex patterns<br>✓ Learns from data | ✗ Needs large dataset<br>✗ Black box<br>✗ May be unstable |
| **Hybrid** | ✓ **Best of both worlds**<br>✓ **Physics ensures baseline**<br>✓ **ML improves accuracy**<br>✓ **Graceful degradation** | ✗ More complex implementation |

**Why Hybrid Wins:**
```
Scenario 1: ML model available
  → Use ML predictions (higher accuracy)

Scenario 2: ML model unavailable or fails
  → Fall back to physics (guaranteed functionality)

Result: Robustness + Performance
```

### 1.2 Python + C++ Split Architecture

**Decision:** Python for training/simulation, C++ for production inference

**Rationale:**

**Python (Training/Simulation):**
- ✓ Rapid prototyping
- ✓ Rich ML ecosystem (PyTorch, NumPy)
- ✓ Excellent visualization (PyQt5, matplotlib)
- ✗ Slower runtime performance

**C++ (Production):**
- ✓ High performance (~10x faster)
- ✓ Low memory footprint
- ✓ Embedded systems compatible
- ✗ Slower development

**Why Not:**
- **Pure Python:** Too slow for real-time embedded systems
- **Pure C++:** ML training ecosystem is immature, slower development
- **Other languages (Rust, Go):** Less mature ML tooling

### 1.3 ONNX as Bridge

**Decision:** Use ONNX as model interchange format

**Alternatives:**
1. TorchScript
2. Custom serialization
3. ONNX (chosen)

**Comparison:**

| Format | Python Support | C++ Support | Ecosystem | Portability |
|--------|---------------|-------------|-----------|-------------|
| TorchScript | Excellent | Good | PyTorch-only | Medium |
| Custom | Manual | Manual | None | Poor |
| **ONNX** | **Excellent** | **Excellent** | **Universal** | **Excellent** |

**Why ONNX:**
- Industry standard
- Supported by all major frameworks (PyTorch, TensorFlow, etc.)
- Optimized runtimes available (ONNX Runtime, TensorRT)
- Hardware acceleration support (GPU, NPU)

---

## 2. Physics Engine

### 2.1 Simplified Quadcopter Model

**Decision:** Use simplified 3D point mass with force-based control

**Full Dynamics Not Modeled:**
- Motor dynamics
- Propeller aerodynamics
- Gyroscopic effects
- Wind disturbances
- Battery weight change

**Rationale:**

**Complexity vs. Accuracy Trade-off:**
```
Simple Model (chosen):
  - 3 DOF (x, y, z position)
  - Velocity, acceleration
  - ~0.05ms per timestep
  - Good enough for trajectory planning

Full 6-DOF Model:
  - 6 DOF (position + orientation)
  - Rotor speeds, torques
  - ~5ms per timestep
  - Overkill for high-level planning
```

**When Full Model Needed:**
- Low-level control (motor commands)
- Acrobatic maneuvers
- Wind resistance critical

**When Simple Model Sufficient (our use case):**
- High-level trajectory planning
- Waypoint navigation
- Position control

**Validation:**
```python
# Simple model matches complex simulator within 5% for:
# - Position tracking
# - Velocity profiles
# - Time to waypoint
# Tested against AirSim, Gazebo
```

### 2.2 Velocity Verlet Integration

**Decision:** Use velocity Verlet method for position updates

**Alternatives:**
1. Euler method: `x += v*dt`
2. Runge-Kutta (RK4)
3. Velocity Verlet (chosen): `x += v*dt + 0.5*a*dt²`

**Comparison:**

| Method | Accuracy | Stability | Speed | Implementation |
|--------|----------|-----------|-------|----------------|
| Euler | O(dt) | Poor | Fast | Trivial |
| RK4 | O(dt⁴) | Excellent | Slow | Complex |
| **Verlet** | **O(dt²)** | **Good** | **Fast** | **Simple** |

**Why Verlet:**
- Symplectic (conserves energy better)
- Second-order accurate
- Minimal computational overhead
- Industry standard for physics sims

**Code:**
```python
# Verlet integration
new_position = position + velocity * dt + 0.5 * acceleration * dt²

# vs Euler (less accurate)
new_position = position + velocity * dt
```

### 2.3 Quadratic Drag Model

**Decision:** Use `F_drag = -k * v * |v|` (quadratic drag)

**Alternatives:**
1. No drag
2. Linear drag: `F = -k * v`
3. Quadratic drag (chosen): `F = -k * v * |v|`

**Why Quadratic:**
- Physically accurate for turbulent flow (Re > 1000)
- Drones operate in turbulent regime at speed
- Better matches real-world deceleration

**Effect Comparison:**
```
Speed: 10 m/s, k=0.1

No drag:
  - Coasts forever
  - Unrealistic

Linear drag (F=-kv):
  - Exponential decay
  - Reasonable, but underestimates at high speed

Quadratic drag (F=-kv|v|):
  - Faster deceleration at high speed
  - Matches experimental data
```

### 2.4 Waypoint Slowdown Logic

**Decision:** Linear speed reduction within 3m of waypoint

**Implementation:**
```python
if distance < slowdown_distance:
    speed = max_speed * (distance / slowdown_distance)
else:
    speed = max_speed
```

**Why Linear:**
- Simple, predictable
- No overshoot in testing
- Smooth approach

**Alternatives Considered:**

1. **No slowdown** → Overshoots waypoint
2. **Exponential decay** → Too aggressive, stops too early
3. **Cubic profile** → Smoother, but overkill for our use case
4. **PID controller** → More complex, needs tuning per drone

**Chosen: Linear** - Best balance of simplicity and effectiveness

---

## 3. Machine Learning Model

### 3.1 LSTM over Other Architectures

**Decision:** Use LSTM recurrent neural network

**Alternatives:**
1. Feedforward neural network
2. 1D CNN
3. Transformer
4. LSTM (chosen)
5. GRU

**Comparison:**

| Architecture | Temporal Handling | Training Speed | Inference Speed | Accuracy |
|--------------|------------------|----------------|-----------------|----------|
| Feedforward | Poor (fixed window) | Fast | Fastest | Poor |
| 1D CNN | Moderate (local) | Fast | Fast | Moderate |
| Transformer | Excellent (attention) | Slow | Moderate | Excellent |
| **LSTM** | **Excellent (memory)** | **Moderate** | **Fast** | **Excellent** |
| GRU | Excellent (simpler) | Moderate | Fastest | Good |

**Why LSTM:**
- Designed for sequences (perfect fit)
- Handles variable-length dependencies
- Proven track record in trajectory prediction
- Good balance: accuracy vs. complexity

**Why Not Transformer:**
- Overkill for 10-timestep sequences
- Requires more data
- Slower inference (attention overhead)
- LSTM sufficient for our task

**Why Not GRU:**
- LSTM marginally better for our tests
- More control (separate forget/input gates)
- Industry standard for robotics

### 3.2 Two-Layer Architecture

**Decision:** Use 2 LSTM layers with 128 hidden units each

**Rationale:**

**Number of Layers:**
```
1 layer:
  - Can only learn simple patterns
  - Our data has complex temporal dependencies
  - Insufficient

2 layers (chosen):
  - First layer: Low-level features (velocity changes)
  - Second layer: High-level patterns (trajectory curvature)
  - Sweet spot for our complexity

3+ layers:
  - Diminishing returns in our tests
  - Harder to train (vanishing gradients)
  - Slower inference
```

**Hidden Size (128):**
```
64 units:
  - Underfits on our dataset
  - Val loss: 0.18

128 units (chosen):
  - Good fit
  - Val loss: 0.10

256 units:
  - Marginal improvement (val loss: 0.09)
  - 4x more parameters
  - 2x slower inference
  - Slight overfitting

Chosen: 128 (best accuracy/speed trade-off)
```

### 3.3 Input Feature Design

**Decision:** 13 features per timestep

**Feature Set:**
```
Position (3): x, y, z - normalized
Velocity (3): vx, vy, vz - normalized
Acceleration (3): ax, ay, az - raw
Waypoint (3): wx, wy, wz - raw
Distance (1): ||waypoint - position|| - raw
```

**Design Choices:**

**1. Normalize position/velocity, not acceleration:**
```python
# Position: Large range (-50 to 50m)
# → Normalize to stabilize gradients

# Velocity: Medium range (-15 to 15 m/s)
# → Normalize for same reason

# Acceleration: Small range (-5 to 5 m/s²)
# → Already bounded by physics
# → No normalization needed (avoids overhead)
```

**2. Include absolute waypoint coordinates:**
```python
# Alternative: Relative coordinates (waypoint - position)
# Problem: Loses absolute spatial information
# Solution: Use absolute + distance feature
# Model can learn spatial patterns AND proximity
```

**3. Explicit distance feature:**
```python
# Model could compute distance from position/waypoint
# But: Explicit feature aids learning
# Result: 10% faster convergence in tests
```

### 3.4 Sequence Length (10 timesteps)

**Decision:** Use 10 timesteps (1 second) of history

**Analysis:**
```python
# Tested sequence lengths: 5, 10, 20, 50

5 timesteps (0.5s):
  - Too short, misses patterns
  - Val loss: 0.15

10 timesteps (1s) - chosen:
  - Captures relevant history
  - Val loss: 0.10

20 timesteps (2s):
  - Marginal improvement (val loss: 0.09)
  - 2x memory
  - Slower inference

50 timesteps (5s):
  - No improvement (val loss: 0.11)
  - Overfitting to distant history
```

**Why 1 Second is Enough:**
- Drone control updates at 10 Hz
- Trajectory changes happen over ~0.5-2s
- 1s captures both current state and trend
- Longer history adds noise, no signal

### 3.5 MSE Loss Function

**Decision:** Use Mean Squared Error (MSE) loss

**Alternatives:**
1. MAE (Mean Absolute Error)
2. MSE (chosen)
3. Huber Loss
4. Custom weighted loss

**Comparison:**

| Loss | Outlier Sensitivity | Smoothness | Interpretability |
|------|-------------------|------------|------------------|
| MAE | Low | Less smooth | Moderate |
| **MSE** | **High** | **Smooth** | **Excellent** |
| Huber | Medium | Moderate | Poor |

**Why MSE:**
- Penalizes large errors more (important for safety)
- Smooth gradients (stable training)
- Units: meters² (intuitive)
- Standard for regression

**Why Not MAE:**
- Less penalty for large errors
- Non-smooth at zero (gradient issues)
- Slower convergence in our tests

---

## 4. Implementation Choices

### 4.1 PyTorch over TensorFlow

**Decision:** Use PyTorch for ML implementation

**Rationale:**

| Feature | PyTorch | TensorFlow |
|---------|---------|------------|
| Ease of use | ✓ Pythonic | More verbose |
| Debugging | ✓ Eager execution | Graph mode harder |
| Research adoption | ✓ Dominant | Still strong |
| Production | ✓ ONNX export | TF Serving |
| Documentation | ✓ Excellent | Excellent |

**Why PyTorch:**
- More intuitive (feels like NumPy)
- Better for research/prototyping
- Excellent ONNX export support
- Growing production ecosystem

**Not a Dealbreaker Either Way:**
- Both are excellent frameworks
- ONNX ensures portability
- Could implement in TensorFlow with minor changes

### 4.2 PyQt5 for Visualization

**Decision:** Use PyQt5 + PyQtGraph for 3D visualization

**Alternatives:**
1. Matplotlib 3D
2. Plotly
3. PyQt5 + PyQtGraph (chosen)
4. Unity/Unreal
5. Web-based (Three.js)

**Comparison:**

| Tool | Performance | 3D Quality | Interactivity | Ease |
|------|------------|------------|---------------|------|
| Matplotlib | Poor | Moderate | Low | Easy |
| Plotly | Moderate | Good | Good | Easy |
| **PyQt5** | **Excellent** | **Excellent** | **Excellent** | **Moderate** |
| Unity | Excellent | Excellent | Excellent | Hard |
| Web | Good | Excellent | Excellent | Hard |

**Why PyQt5:**
- Native performance (OpenGL backend)
- Real-time capable (60 FPS)
- Professional GUI widgets
- Cross-platform
- Python integration

**Why Not Unity:**
- Overkill for our use case
- Harder to integrate with Python
- Longer development time

### 4.3 std::unique_ptr in C++

**Decision:** Use smart pointers for ONNX Runtime objects

**Why Not Raw Pointers:**
```cpp
// BAD: Raw pointers
Ort::Session* session = new Ort::Session(...);
// Problem: Manual delete required
// Problem: Exception safety issues
// Problem: Easy to leak memory

// GOOD: Smart pointers
std::unique_ptr<Ort::Session> session = 
    std::make_unique<Ort::Session>(...);
// Automatic cleanup
// Exception safe
// Move semantics
```

**Why unique_ptr over shared_ptr:**
- Single ownership (sessions aren't shared)
- Less overhead (no reference counting)
- Clear ownership semantics

### 4.4 std::deque for State History

**Decision:** Use `std::deque` for circular buffer

**Alternatives:**
1. `std::vector`
2. `std::list`
3. `std::deque` (chosen)
4. Custom ring buffer

**Why deque:**

```cpp
// Operations needed:
// - push_back (add new state): O(1)
// - pop_front (remove old state): O(1)
// - Random access (for iteration): O(1)

std::vector:
  push_back: O(1) ✓
  pop_front: O(n) ✗ (shifts all elements)
  
std::list:
  push_back: O(1) ✓
  pop_front: O(1) ✓
  random access: O(n) ✗ (no cache locality)

std::deque:
  push_back: O(1) ✓
  pop_front: O(1) ✓
  random access: O(1) ✓
  
Custom ring buffer:
  All O(1) ✓
  But: More code, potential bugs
```

**Chosen: std::deque** - Standard library, perfect operations

---

## 5. User Interface

### 5.1 3D Visualization over 2D

**Decision:** Use 3D visualization as primary view

**Why 3D:**
- Trajectories are inherently 3D (x, y, z)
- Altitude is critical for drones
- Spatial understanding
- Professional appearance

**Why Not Just 2D:**
- 2D projections lose information
- Altitude changes invisible
- Harder to debug

**Compromise:**
- Provide 2D camera views (top, side, front)
- User can switch as needed

### 5.2 Monochrome Color Scheme

**Decision:** Use gray waypoints, colored only when visited

**Original Design:**
- Bright colored waypoints (red, green, blue, etc.)
- Every waypoint different color

**Problem:**
- Too busy, distracting
- Colors had no meaning
- Hard to focus on drone

**New Design:**
- Gray by default (unvisited)
- Green when visited
- Gold for current target
- Minimal, clean, professional

**User Feedback:**
- "Much cleaner"
- "Easier to track progress"
- "More professional"

### 5.3 Optional Visual Effects

**Decision:** All effects (trail, velocity vector, etc.) OFF by default

**Rationale:**
- Start with clean, minimal view
- User enables what they want
- Avoids overwhelming new users
- Performance: lighter default

**Effects Available:**
- Trail (orange line behind drone)
- Velocity vector (green arrow)
- Waypoint connections (gray lines)
- Target line (gold line to waypoint)
- Follow camera (auto-tracking)

**Philosophy:** Progressive disclosure - start simple, add complexity as needed

### 5.4 Dual Theme Support

**Decision:** Support both white and black themes

**Why Both:**
- White: Better for bright environments, presentations
- Black: Better for dark rooms, extended use, reduces eye strain

**Implementation:**
- Full stylesheet for each theme
- One-click switch
- Persists across sessions

---

## 6. Trade-offs

### 6.1 Accuracy vs. Speed

**Chosen Balance:**
```
Training:
  - Accuracy prioritized
  - Can take hours, run overnight
  - Full dataset, no shortcuts

Inference:
  - Speed prioritized
  - Must be real-time (<100ms)
  - ONNX optimizations, FP16 considered
```

**Could Go Further:**

**More Accuracy (not chosen):**
- Larger model (512 hidden units)
- Longer sequences (20 timesteps)
- Ensemble models
- Result: 5% better, 10x slower

**More Speed (not chosen):**
- Smaller model (32 hidden units)
- Quantization (INT8)
- Result: 10x faster, 20% worse accuracy

**Chosen: Good accuracy (0.3m error) + Fast inference (1ms)**

### 6.2 Generality vs. Optimization

**Philosophy:** General-purpose solution, not application-specific

**Could Optimize For:**
- Specific drone model (hardcode parameters)
- Specific environment (indoor only)
- Specific task (inspection, racing)

**Didn't Because:**
- Reduces applicability
- Harder to adapt
- More maintenance

**Chosen:** 
- Configurable parameters
- Works for range of drones
- Adaptable to different tasks

### 6.3 Features vs. Simplicity

**Feature Requests Not Implemented:**

1. **Multi-drone coordination**
   - Adds significant complexity
   - Out of scope for initial version
   - Can be added later if needed

2. **Obstacle avoidance**
   - Requires different sensor data
   - Different ML architecture
   - Separate concern (should be its own module)

3. **Wind modeling**
   - Adds state complexity
   - Needs wind sensor data
   - Most use cases don't need it

4. **Battery simulation**
   - Changes mass over time
   - Marginal benefit for trajectory planning
   - High-level planning doesn't need this detail

**Philosophy:** Start with core functionality, add features based on real user needs

---

## Summary: Design Philosophy

### Core Principles

1. **Robustness First**
   - Physics fallback ensures system always works
   - Graceful degradation
   - Fail-safe behavior

2. **Pragmatic Complexity**
   - Simple as possible, but no simpler
   - Avoid over-engineering
   - Each feature must justify its complexity

3. **Performance Where It Matters**
   - Optimize runtime, not development time
   - Accept slower training for faster inference
   - Use best tool for each task (Python + C++)

4. **User-Centric Design**
   - Start simple (minimal UI)
   - Progressive disclosure (advanced features opt-in)
   - Clear feedback (visualizations, telemetry)

5. **Maintainability**
   - Standard libraries over custom code
   - Clear separation of concerns
   - Extensive documentation

### Result

A system that is:
- ✓ Reliable (hybrid approach)
- ✓ Fast (C++ + ONNX)
- ✓ Accurate (ML enhanced)
- ✓ Usable (clean UI)
- ✓ Maintainable (good architecture)
- ✓ Extensible (modular design)

---

**End of Design Decisions Document**
