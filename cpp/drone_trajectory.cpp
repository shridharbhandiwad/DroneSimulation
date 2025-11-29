/**
 * Drone Trajectory Predictor - C++ Implementation
 */

#include "drone_trajectory.h"
#include <cmath>
#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>

namespace drone {

// ============================================================================
// Vec3 Implementation
// ============================================================================

float Vec3::norm() const {
    return std::sqrt(x*x + y*y + z*z);
}

Vec3 Vec3::normalized() const {
    float n = norm();
    if (n < 1e-6f) return *this;
    return Vec3(x/n, y/n, z/n);
}

Vec3 Vec3::operator+(const Vec3& other) const {
    return Vec3(x + other.x, y + other.y, z + other.z);
}

Vec3 Vec3::operator-(const Vec3& other) const {
    return Vec3(x - other.x, y - other.y, z - other.z);
}

Vec3 Vec3::operator*(float scalar) const {
    return Vec3(x * scalar, y * scalar, z * scalar);
}

// ============================================================================
// NormalizationParams Implementation
// ============================================================================

NormalizationParams::NormalizationParams() {
    pos_mean = Vec3(0, 0, 0);
    pos_std = Vec3(1, 1, 1);
    vel_mean = Vec3(0, 0, 0);
    vel_std = Vec3(1, 1, 1);
}

bool NormalizationParams::loadFromFile(const std::string& filepath) {
    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Error: Cannot open normalization file: " << filepath << std::endl;
        return false;
    }
    
    std::string line;
    while (std::getline(file, line)) {
        // Skip comments and empty lines
        if (line.empty() || line[0] == '#') continue;
        
        std::istringstream iss(line);
        std::string key;
        iss >> key;
        
        if (key == "pos_mean:") {
            iss >> pos_mean.x >> pos_mean.y >> pos_mean.z;
        } else if (key == "pos_std:") {
            iss >> pos_std.x >> pos_std.y >> pos_std.z;
        } else if (key == "vel_mean:") {
            iss >> vel_mean.x >> vel_mean.y >> vel_mean.z;
        } else if (key == "vel_std:") {
            iss >> vel_std.x >> vel_std.y >> vel_std.z;
        }
    }
    
    file.close();
    return true;
}

// ============================================================================
// TrajectoryPredictor Implementation
// ============================================================================

TrajectoryPredictor::TrajectoryPredictor(const std::string& model_path,
                                       const std::string& normalization_path,
                                       int sequence_length)
    : model_path_(model_path),
      normalization_path_(normalization_path),
      sequence_length_(sequence_length),
      input_size_(13),
      output_size_(6) {
}

TrajectoryPredictor::~TrajectoryPredictor() {
}

bool TrajectoryPredictor::initialize() {
    try {
        // Load normalization parameters
        if (!norm_params_.loadFromFile(normalization_path_)) {
            std::cerr << "Failed to load normalization parameters" << std::endl;
            return false;
        }
        
        // Initialize ONNX Runtime
        env_ = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "DroneTrajectory");
        
        session_options_ = std::make_unique<Ort::SessionOptions>();
        session_options_->SetIntraOpNumThreads(1);
        session_options_->SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_ALL);
        
        // Create session
        session_ = std::make_unique<Ort::Session>(*env_, model_path_.c_str(), *session_options_);
        
        // Get input/output names
        input_names_.push_back("input_sequence");
        output_names_.push_back("output");
        
        std::cout << "ONNX model loaded successfully: " << model_path_ << std::endl;
        
        return true;
        
    } catch (const Ort::Exception& e) {
        std::cerr << "ONNX Runtime error: " << e.what() << std::endl;
        return false;
    } catch (const std::exception& e) {
        std::cerr << "Error initializing predictor: " << e.what() << std::endl;
        return false;
    }
}

void TrajectoryPredictor::addState(const DroneState& state) {
    state_history_.push_back(state);
    
    // Keep only the required history length
    while (state_history_.size() > static_cast<size_t>(sequence_length_)) {
        state_history_.pop_front();
    }
}

bool TrajectoryPredictor::isReady() const {
    return state_history_.size() >= static_cast<size_t>(sequence_length_);
}

std::vector<float> TrajectoryPredictor::prepareInput(const Vec3& target_waypoint) {
    std::vector<float> input_data;
    input_data.reserve(sequence_length_ * input_size_);
    
    // If we don't have enough history, pad with first available state
    size_t history_size = state_history_.size();
    size_t pad_count = (history_size < static_cast<size_t>(sequence_length_)) 
                       ? sequence_length_ - history_size : 0;
    
    // Pad with first state if necessary
    if (pad_count > 0 && history_size > 0) {
        const DroneState& first_state = state_history_.front();
        Vec3 pos = first_state.position;
        Vec3 vel = first_state.velocity;
        normalizePosition(pos);
        normalizeVelocity(vel);
        float dist = calculateDistance(first_state.position, target_waypoint);
        
        for (size_t i = 0; i < pad_count; ++i) {
            input_data.push_back(pos.x);
            input_data.push_back(pos.y);
            input_data.push_back(pos.z);
            input_data.push_back(vel.x);
            input_data.push_back(vel.y);
            input_data.push_back(vel.z);
            input_data.push_back(first_state.acceleration.x);
            input_data.push_back(first_state.acceleration.y);
            input_data.push_back(first_state.acceleration.z);
            input_data.push_back(target_waypoint.x);
            input_data.push_back(target_waypoint.y);
            input_data.push_back(target_waypoint.z);
            input_data.push_back(dist);
        }
    }
    
    // Add actual history
    for (const auto& state : state_history_) {
        Vec3 pos = state.position;
        Vec3 vel = state.velocity;
        normalizePosition(pos);
        normalizeVelocity(vel);
        float dist = calculateDistance(state.position, target_waypoint);
        
        // Position (normalized)
        input_data.push_back(pos.x);
        input_data.push_back(pos.y);
        input_data.push_back(pos.z);
        
        // Velocity (normalized)
        input_data.push_back(vel.x);
        input_data.push_back(vel.y);
        input_data.push_back(vel.z);
        
        // Acceleration (not normalized)
        input_data.push_back(state.acceleration.x);
        input_data.push_back(state.acceleration.y);
        input_data.push_back(state.acceleration.z);
        
        // Target waypoint
        input_data.push_back(target_waypoint.x);
        input_data.push_back(target_waypoint.y);
        input_data.push_back(target_waypoint.z);
        
        // Distance to waypoint
        input_data.push_back(dist);
    }
    
    return input_data;
}

bool TrajectoryPredictor::predict(const Vec3& target_waypoint, DroneState& predicted_state) {
    if (!isReady()) {
        std::cerr << "Not enough history for prediction (need " << sequence_length_ 
                  << ", have " << state_history_.size() << ")" << std::endl;
        return false;
    }
    
    try {
        // Prepare input
        std::vector<float> input_data = prepareInput(target_waypoint);
        
        // Create input tensor
        std::vector<int64_t> input_shape = {1, sequence_length_, input_size_};
        auto memory_info = Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);
        Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
            memory_info, input_data.data(), input_data.size(),
            input_shape.data(), input_shape.size()
        );
        
        // Run inference
        auto output_tensors = session_->Run(
            Ort::RunOptions{nullptr},
            input_names_.data(),
            &input_tensor,
            1,
            output_names_.data(),
            1
        );
        
        // Get output
        float* output_data = output_tensors[0].GetTensorMutableData<float>();
        
        // Extract prediction
        Vec3 pred_pos(output_data[0], output_data[1], output_data[2]);
        Vec3 pred_vel(output_data[3], output_data[4], output_data[5]);
        
        // Denormalize
        denormalizePosition(pred_pos);
        denormalizeVelocity(pred_vel);
        
        // Fill predicted state
        predicted_state.position = pred_pos;
        predicted_state.velocity = pred_vel;
        
        // Calculate acceleration from velocity change
        if (!state_history_.empty()) {
            const DroneState& last_state = state_history_.back();
            float dt = 0.1f; // 100ms
            predicted_state.acceleration = (pred_vel - last_state.velocity) * (1.0f / dt);
            predicted_state.timestamp = last_state.timestamp + dt;
        }
        
        return true;
        
    } catch (const Ort::Exception& e) {
        std::cerr << "ONNX inference error: " << e.what() << std::endl;
        return false;
    } catch (const std::exception& e) {
        std::cerr << "Prediction error: " << e.what() << std::endl;
        return false;
    }
}

void TrajectoryPredictor::reset() {
    state_history_.clear();
}

void TrajectoryPredictor::normalizePosition(Vec3& pos) const {
    pos.x = (pos.x - norm_params_.pos_mean.x) / (norm_params_.pos_std.x + 1e-6f);
    pos.y = (pos.y - norm_params_.pos_mean.y) / (norm_params_.pos_std.y + 1e-6f);
    pos.z = (pos.z - norm_params_.pos_mean.z) / (norm_params_.pos_std.z + 1e-6f);
}

void TrajectoryPredictor::normalizeVelocity(Vec3& vel) const {
    vel.x = (vel.x - norm_params_.vel_mean.x) / (norm_params_.vel_std.x + 1e-6f);
    vel.y = (vel.y - norm_params_.vel_mean.y) / (norm_params_.vel_std.y + 1e-6f);
    vel.z = (vel.z - norm_params_.vel_mean.z) / (norm_params_.vel_std.z + 1e-6f);
}

void TrajectoryPredictor::denormalizePosition(Vec3& pos) const {
    pos.x = pos.x * (norm_params_.pos_std.x + 1e-6f) + norm_params_.pos_mean.x;
    pos.y = pos.y * (norm_params_.pos_std.y + 1e-6f) + norm_params_.pos_mean.y;
    pos.z = pos.z * (norm_params_.pos_std.z + 1e-6f) + norm_params_.pos_mean.z;
}

void TrajectoryPredictor::denormalizeVelocity(Vec3& vel) const {
    vel.x = vel.x * (norm_params_.vel_std.x + 1e-6f) + norm_params_.vel_mean.x;
    vel.y = vel.y * (norm_params_.vel_std.y + 1e-6f) + norm_params_.vel_mean.y;
    vel.z = vel.z * (norm_params_.vel_std.z + 1e-6f) + norm_params_.vel_mean.z;
}

float TrajectoryPredictor::calculateDistance(const Vec3& a, const Vec3& b) const {
    Vec3 diff = b - a;
    return diff.norm();
}

// ============================================================================
// PhysicsTrajectoryGenerator Implementation
// ============================================================================

PhysicsTrajectoryGenerator::PhysicsTrajectoryGenerator(float max_speed,
                                                       float max_acceleration,
                                                       float max_vertical_speed)
    : max_speed_(max_speed),
      max_acceleration_(max_acceleration),
      max_vertical_speed_(max_vertical_speed),
      drag_coefficient_(0.1f) {
}

void PhysicsTrajectoryGenerator::update(const DroneState& current_state,
                                       const Vec3& target_waypoint,
                                       float dt,
                                       DroneState& next_state) {
    // Calculate direction to target
    Vec3 to_target = target_waypoint - current_state.position;
    float distance = to_target.norm();
    
    Vec3 target_velocity;
    
    if (distance < 0.1f) {
        // Reached waypoint
        target_velocity = Vec3(0, 0, 0);
    } else {
        Vec3 direction = to_target.normalized();
        
        // Desired speed based on distance (slow down near target)
        float desired_speed = std::min(max_speed_, distance / 2.0f);
        target_velocity = direction * desired_speed;
        
        // Limit vertical speed
        target_velocity.z = std::clamp(target_velocity.z, -max_vertical_speed_, max_vertical_speed_);
    }
    
    // Apply acceleration limits
    Vec3 velocity_change = target_velocity - current_state.velocity;
    float max_change = max_acceleration_ * dt;
    float change_magnitude = velocity_change.norm();
    
    if (change_magnitude > max_change) {
        velocity_change = velocity_change.normalized() * max_change;
    }
    
    Vec3 new_velocity = current_state.velocity + velocity_change;
    
    // Apply drag
    float vel_mag = new_velocity.norm();
    Vec3 drag = new_velocity * (-drag_coefficient_ * vel_mag);
    new_velocity = new_velocity + drag * dt;
    
    // Calculate acceleration
    Vec3 acceleration = (new_velocity - current_state.velocity) * (1.0f / dt);
    
    // Update position
    Vec3 new_position = current_state.position + new_velocity * dt + 
                       acceleration * (0.5f * dt * dt);
    
    // Fill next state
    next_state.position = new_position;
    next_state.velocity = new_velocity;
    next_state.acceleration = acceleration;
    next_state.timestamp = current_state.timestamp + dt;
}

} // namespace drone
