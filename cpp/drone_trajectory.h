/**
 * Drone Trajectory Predictor - C++ Header
 * 
 * Real-time trajectory prediction using ONNX Runtime
 */

#ifndef DRONE_TRAJECTORY_H
#define DRONE_TRAJECTORY_H

#include <vector>
#include <string>
#include <memory>
#include <deque>
#include <onnxruntime_cxx_api.h>

namespace drone {

/**
 * 3D vector structure for position/velocity/acceleration
 */
struct Vec3 {
    float x, y, z;
    
    Vec3() : x(0), y(0), z(0) {}
    Vec3(float x_, float y_, float z_) : x(x_), y(y_), z(z_) {}
    
    float norm() const;
    Vec3 normalized() const;
    Vec3 operator+(const Vec3& other) const;
    Vec3 operator-(const Vec3& other) const;
    Vec3 operator*(float scalar) const;
};

/**
 * Drone state at a single timestep
 */
struct DroneState {
    Vec3 position;
    Vec3 velocity;
    Vec3 acceleration;
    double timestamp;
    
    DroneState() : timestamp(0.0) {}
};

/**
 * Normalization parameters for input/output data
 */
struct NormalizationParams {
    Vec3 pos_mean;
    Vec3 pos_std;
    Vec3 vel_mean;
    Vec3 vel_std;
    
    NormalizationParams();
    bool loadFromFile(const std::string& filepath);
};

/**
 * Drone Trajectory Predictor using ONNX Runtime
 * 
 * This class provides real-time trajectory prediction using a trained
 * LSTM model exported to ONNX format.
 */
class TrajectoryPredictor {
public:
    /**
     * Constructor
     * 
     * @param model_path Path to ONNX model file
     * @param normalization_path Path to normalization parameters file
     * @param sequence_length Length of input sequence (default: 10)
     */
    TrajectoryPredictor(const std::string& model_path,
                       const std::string& normalization_path,
                       int sequence_length = 10);
    
    /**
     * Destructor
     */
    ~TrajectoryPredictor();
    
    /**
     * Initialize the predictor
     * 
     * @return true if successful, false otherwise
     */
    bool initialize();
    
    /**
     * Add a new state to the history buffer
     * 
     * @param state Current drone state
     */
    void addState(const DroneState& state);
    
    /**
     * Predict next state given current history and target waypoint
     * 
     * @param target_waypoint Target waypoint position
     * @param predicted_state Output predicted state
     * @return true if successful, false otherwise
     */
    bool predict(const Vec3& target_waypoint, DroneState& predicted_state);
    
    /**
     * Reset the state history buffer
     */
    void reset();
    
    /**
     * Get the current sequence length
     */
    int getSequenceLength() const { return sequence_length_; }
    
    /**
     * Check if predictor is ready (has enough history)
     */
    bool isReady() const;

private:
    // Model paths
    std::string model_path_;
    std::string normalization_path_;
    
    // Model parameters
    int sequence_length_;
    int input_size_;
    int output_size_;
    
    // ONNX Runtime components
    std::unique_ptr<Ort::Env> env_;
    std::unique_ptr<Ort::Session> session_;
    std::unique_ptr<Ort::SessionOptions> session_options_;
    Ort::AllocatorWithDefaultOptions allocator_;
    
    // Input/output names
    std::vector<const char*> input_names_;
    std::vector<const char*> output_names_;
    
    // State history
    std::deque<DroneState> state_history_;
    
    // Normalization parameters
    NormalizationParams norm_params_;
    
    // Helper functions
    std::vector<float> prepareInput(const Vec3& target_waypoint);
    void normalizePosition(Vec3& pos) const;
    void normalizeVelocity(Vec3& vel) const;
    void denormalizePosition(Vec3& pos) const;
    void denormalizeVelocity(Vec3& vel) const;
    float calculateDistance(const Vec3& a, const Vec3& b) const;
};

/**
 * Physics-based trajectory generator (fallback when ML not available)
 */
class PhysicsTrajectoryGenerator {
public:
    PhysicsTrajectoryGenerator(float max_speed = 15.0f,
                              float max_acceleration = 5.0f,
                              float max_vertical_speed = 5.0f);
    
    /**
     * Update state for one timestep
     * 
     * @param current_state Current drone state
     * @param target_waypoint Target position
     * @param dt Time step in seconds
     * @param next_state Output next state
     */
    void update(const DroneState& current_state,
               const Vec3& target_waypoint,
               float dt,
               DroneState& next_state);

private:
    float max_speed_;
    float max_acceleration_;
    float max_vertical_speed_;
    float drag_coefficient_;
};

} // namespace drone

#endif // DRONE_TRAJECTORY_H
