/**
 * Example usage of Drone Trajectory Predictor in C++
 */

#include "drone_trajectory.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <thread>
#include <iomanip>

using namespace drone;

void printState(const DroneState& state, const std::string& label) {
    std::cout << label << ":" << std::endl;
    std::cout << "  Position: (" << std::fixed << std::setprecision(2)
              << state.position.x << ", " << state.position.y << ", " 
              << state.position.z << ")" << std::endl;
    std::cout << "  Velocity: (" << state.velocity.x << ", " 
              << state.velocity.y << ", " << state.velocity.z << ")" << std::endl;
    std::cout << "  Time: " << state.timestamp << "s" << std::endl;
}

void runMLPrediction(const std::string& model_path, 
                     const std::string& norm_path) {
    std::cout << "\n========================================" << std::endl;
    std::cout << "Running ML-based Trajectory Prediction" << std::endl;
    std::cout << "========================================\n" << std::endl;
    
    // Create predictor
    TrajectoryPredictor predictor(model_path, norm_path, 10);
    
    if (!predictor.initialize()) {
        std::cerr << "Failed to initialize predictor" << std::endl;
        return;
    }
    
    // Define initial state
    DroneState current_state;
    current_state.position = Vec3(0, 0, 5);
    current_state.velocity = Vec3(0, 0, 0);
    current_state.acceleration = Vec3(0, 0, 0);
    current_state.timestamp = 0.0;
    
    // Define waypoints
    std::vector<Vec3> waypoints = {
        Vec3(10, 10, 8),
        Vec3(20, 5, 10),
        Vec3(15, -10, 7),
        Vec3(0, 0, 5)
    };
    
    size_t current_waypoint_idx = 0;
    Vec3 target = waypoints[current_waypoint_idx];
    
    std::cout << "Initial state:" << std::endl;
    printState(current_state, "State");
    
    // Build up history first
    std::cout << "\nBuilding state history..." << std::endl;
    PhysicsTrajectoryGenerator physics_gen;
    
    for (int i = 0; i < predictor.getSequenceLength(); ++i) {
        predictor.addState(current_state);
        
        DroneState next_state;
        physics_gen.update(current_state, target, 0.1f, next_state);
        current_state = next_state;
    }
    
    std::cout << "History built. Starting ML prediction...\n" << std::endl;
    
    // Now use ML predictor
    int max_steps = 300; // 30 seconds
    
    for (int step = 0; step < max_steps; ++step) {
        // Check if reached current waypoint
        Vec3 to_target = target - current_state.position;
        float dist = to_target.norm();
        
        if (dist < 0.5f) {
            current_waypoint_idx++;
            if (current_waypoint_idx >= waypoints.size()) {
                std::cout << "\nReached all waypoints!" << std::endl;
                break;
            }
            target = waypoints[current_waypoint_idx];
            std::cout << "\nMoving to waypoint #" << current_waypoint_idx + 1 
                     << ": (" << target.x << ", " << target.y << ", " 
                     << target.z << ")" << std::endl;
        }
        
        // Predict next state
        DroneState predicted_state;
        if (predictor.predict(target, predicted_state)) {
            current_state = predicted_state;
            predictor.addState(current_state);
            
            // Print every 10 steps (1 second)
            if (step % 10 == 0) {
                std::cout << "Step " << step << " (t=" << current_state.timestamp 
                         << "s) - Distance to target: " << dist << "m" << std::endl;
            }
        } else {
            std::cerr << "Prediction failed at step " << step << std::endl;
            break;
        }
        
        // Simulate real-time (100ms delay)
        // std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    std::cout << "\nFinal state:" << std::endl;
    printState(current_state, "State");
}

void runPhysicsPrediction() {
    std::cout << "\n========================================" << std::endl;
    std::cout << "Running Physics-based Trajectory" << std::endl;
    std::cout << "========================================\n" << std::endl;
    
    PhysicsTrajectoryGenerator physics;
    
    // Define initial state
    DroneState current_state;
    current_state.position = Vec3(0, 0, 5);
    current_state.velocity = Vec3(0, 0, 0);
    current_state.acceleration = Vec3(0, 0, 0);
    current_state.timestamp = 0.0;
    
    // Define waypoints
    std::vector<Vec3> waypoints = {
        Vec3(10, 10, 8),
        Vec3(20, 5, 10),
        Vec3(15, -10, 7),
        Vec3(0, 0, 5)
    };
    
    size_t current_waypoint_idx = 0;
    Vec3 target = waypoints[current_waypoint_idx];
    
    std::cout << "Initial state:" << std::endl;
    printState(current_state, "State");
    std::cout << std::endl;
    
    int max_steps = 300;
    float dt = 0.1f; // 100ms
    
    for (int step = 0; step < max_steps; ++step) {
        // Check if reached current waypoint
        Vec3 to_target = target - current_state.position;
        float dist = to_target.norm();
        
        if (dist < 0.5f) {
            current_waypoint_idx++;
            if (current_waypoint_idx >= waypoints.size()) {
                std::cout << "Reached all waypoints!" << std::endl;
                break;
            }
            target = waypoints[current_waypoint_idx];
            std::cout << "Moving to waypoint #" << current_waypoint_idx + 1 
                     << ": (" << target.x << ", " << target.y << ", " 
                     << target.z << ")" << std::endl;
        }
        
        // Update state
        DroneState next_state;
        physics.update(current_state, target, dt, next_state);
        current_state = next_state;
        
        // Print every 10 steps
        if (step % 10 == 0) {
            std::cout << "Step " << step << " (t=" << current_state.timestamp 
                     << "s) - Distance to target: " << dist << "m" << std::endl;
        }
    }
    
    std::cout << "\nFinal state:" << std::endl;
    printState(current_state, "State");
}

void performanceBenchmark(const std::string& model_path, 
                         const std::string& norm_path) {
    std::cout << "\n========================================" << std::endl;
    std::cout << "Performance Benchmark" << std::endl;
    std::cout << "========================================\n" << std::endl;
    
    TrajectoryPredictor predictor(model_path, norm_path, 10);
    
    if (!predictor.initialize()) {
        std::cerr << "Failed to initialize predictor" << std::endl;
        return;
    }
    
    // Setup initial state
    DroneState state;
    state.position = Vec3(0, 0, 5);
    state.velocity = Vec3(1, 1, 0);
    state.acceleration = Vec3(0, 0, 0);
    state.timestamp = 0.0;
    
    // Build history
    for (int i = 0; i < predictor.getSequenceLength(); ++i) {
        predictor.addState(state);
        state.timestamp += 0.1;
    }
    
    Vec3 target(10, 10, 8);
    DroneState predicted;
    
    // Warmup
    for (int i = 0; i < 10; ++i) {
        predictor.predict(target, predicted);
    }
    
    // Benchmark
    int num_iterations = 1000;
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < num_iterations; ++i) {
        predictor.predict(target, predicted);
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    double avg_time_us = duration.count() / (double)num_iterations;
    double avg_time_ms = avg_time_us / 1000.0;
    double fps = 1000000.0 / avg_time_us;
    
    std::cout << "Benchmark Results (" << num_iterations << " iterations):" << std::endl;
    std::cout << "  Average inference time: " << std::fixed << std::setprecision(3) 
              << avg_time_ms << " ms" << std::endl;
    std::cout << "  Inference rate: " << std::setprecision(1) << fps << " Hz" << std::endl;
    std::cout << "  Real-time capable: " << (avg_time_ms < 100 ? "YES" : "NO") 
              << " (need < 100ms for 10Hz)" << std::endl;
}

int main(int argc, char** argv) {
    std::cout << "Drone Trajectory Prediction - C++ Demo" << std::endl;
    std::cout << "======================================\n" << std::endl;
    
    // Paths to model files
    std::string model_path = "../models/drone_trajectory.onnx";
    std::string norm_path = "../models/drone_trajectory_normalization.txt";
    
    // Check if model files exist
    bool ml_available = true;
    std::ifstream model_file(model_path);
    std::ifstream norm_file(norm_path);
    
    if (!model_file.good() || !norm_file.good()) {
        std::cout << "Warning: ML model files not found." << std::endl;
        std::cout << "  Expected: " << model_path << std::endl;
        std::cout << "  Expected: " << norm_path << std::endl;
        std::cout << "\nPlease run the Python training pipeline first:" << std::endl;
        std::cout << "  1. cd python" << std::endl;
        std::cout << "  2. python data_generator.py" << std::endl;
        std::cout << "  3. python train_model.py" << std::endl;
        std::cout << "  4. python export_to_onnx.py" << std::endl;
        std::cout << "\nFalling back to physics-based trajectory only.\n" << std::endl;
        ml_available = false;
    }
    
    if (ml_available) {
        // Run ML-based prediction
        runMLPrediction(model_path, norm_path);
        
        // Run performance benchmark
        performanceBenchmark(model_path, norm_path);
    }
    
    // Always run physics-based for comparison
    runPhysicsPrediction();
    
    std::cout << "\nDemo complete!" << std::endl;
    
    return 0;
}
