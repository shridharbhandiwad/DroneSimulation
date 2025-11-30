/**
 * Example usage of Drone Trajectory Predictor in C++
 * Enhanced with dynamic waypoint input and detailed trajectory output
 */

#include "drone_trajectory.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <thread>
#include <iomanip>
#include <sstream>
#include <limits>

using namespace drone;

// ============================================================================
// Output and Display Functions
// ============================================================================

void printState(const DroneState& state, const std::string& label) {
    std::cout << label << ":" << std::endl;
    std::cout << "  Position: (" << std::fixed << std::setprecision(2)
              << state.position.x << ", " << state.position.y << ", " 
              << state.position.z << ")" << std::endl;
    std::cout << "  Velocity: (" << state.velocity.x << ", " 
              << state.velocity.y << ", " << state.velocity.z << ")" << std::endl;
    std::cout << "  Time: " << state.timestamp << "s" << std::endl;
}

void printDetailedState(const DroneState& state, int step, const Vec3& target) {
    Vec3 to_target = target - state.position;
    float dist = to_target.norm();
    float speed = state.velocity.norm();
    
    std::cout << std::fixed << std::setprecision(3);
    std::cout << "Step " << std::setw(4) << step 
              << " | t=" << std::setw(6) << state.timestamp << "s"
              << " | Pos: (" << std::setw(7) << state.position.x 
              << ", " << std::setw(7) << state.position.y 
              << ", " << std::setw(7) << state.position.z << ")"
              << " | Vel: (" << std::setw(6) << state.velocity.x
              << ", " << std::setw(6) << state.velocity.y
              << ", " << std::setw(6) << state.velocity.z << ")"
              << " | Speed: " << std::setw(6) << speed << " m/s"
              << " | Dist: " << std::setw(6) << dist << " m"
              << std::endl;
}

void printWaypoints(const std::vector<Vec3>& waypoints) {
    std::cout << "\n=== Waypoint List ===" << std::endl;
    for (size_t i = 0; i < waypoints.size(); ++i) {
        std::cout << "  Waypoint " << (i + 1) << ": ("
                  << std::fixed << std::setprecision(2)
                  << waypoints[i].x << ", "
                  << waypoints[i].y << ", "
                  << waypoints[i].z << ")" << std::endl;
    }
    std::cout << "=====================\n" << std::endl;
}

// ============================================================================
// Interactive Input Functions
// ============================================================================

void clearInputBuffer() {
    std::cin.clear();
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
}

Vec3 inputWaypoint(int index) {
    float x, y, z;
    std::cout << "Enter waypoint " << index << " coordinates (x y z): ";
    
    while (!(std::cin >> x >> y >> z)) {
        std::cout << "Invalid input! Please enter three numbers (x y z): ";
        clearInputBuffer();
    }
    
    return Vec3(x, y, z);
}

std::vector<Vec3> getDynamicWaypoints() {
    std::vector<Vec3> waypoints;
    int num_waypoints;
    
    std::cout << "\n=== Dynamic Waypoint Input ===" << std::endl;
    std::cout << "How many waypoints do you want to add? ";
    
    while (!(std::cin >> num_waypoints) || num_waypoints <= 0 || num_waypoints > 100) {
        std::cout << "Please enter a valid number (1-100): ";
        clearInputBuffer();
    }
    
    std::cout << "\nEnter waypoints in format: x y z (separated by spaces)" << std::endl;
    std::cout << "Example: 10.5 20.0 8.5\n" << std::endl;
    
    for (int i = 1; i <= num_waypoints; ++i) {
        Vec3 wp = inputWaypoint(i);
        waypoints.push_back(wp);
        std::cout << "  Added: (" << wp.x << ", " << wp.y << ", " << wp.z << ")\n" << std::endl;
    }
    
    return waypoints;
}

bool askYesNo(const std::string& question) {
    std::cout << question << " (y/n): ";
    char response;
    std::cin >> response;
    return (response == 'y' || response == 'Y');
}

// ============================================================================
// CSV Export Function
// ============================================================================

class TrajectoryLogger {
public:
    TrajectoryLogger(const std::string& filename) 
        : filename_(filename), file_(filename) {
        if (file_.is_open()) {
            // Write CSV header
            file_ << "step,time,pos_x,pos_y,pos_z,vel_x,vel_y,vel_z,"
                  << "acc_x,acc_y,acc_z,speed,distance_to_target,"
                  << "target_x,target_y,target_z\n";
        }
    }
    
    ~TrajectoryLogger() {
        if (file_.is_open()) {
            file_.close();
            std::cout << "\nTrajectory data saved to: " << filename_ << std::endl;
        }
    }
    
    void log(int step, const DroneState& state, const Vec3& target) {
        if (!file_.is_open()) return;
        
        Vec3 to_target = target - state.position;
        float dist = to_target.norm();
        float speed = state.velocity.norm();
        
        file_ << step << ","
              << state.timestamp << ","
              << state.position.x << "," << state.position.y << "," << state.position.z << ","
              << state.velocity.x << "," << state.velocity.y << "," << state.velocity.z << ","
              << state.acceleration.x << "," << state.acceleration.y << "," << state.acceleration.z << ","
              << speed << "," << dist << ","
              << target.x << "," << target.y << "," << target.z << "\n";
    }
    
    bool isOpen() const { return file_.is_open(); }
    
private:
    std::string filename_;
    std::ofstream file_;
};

// ============================================================================
// Interactive Trajectory Simulation
// ============================================================================

void runInteractiveTrajectory(TrajectoryPredictor* predictor = nullptr) {
    std::cout << "\n========================================" << std::endl;
    std::cout << "Interactive Trajectory Simulation" << std::endl;
    std::cout << "========================================\n" << std::endl;
    
    // Get waypoints from user
    std::vector<Vec3> waypoints = getDynamicWaypoints();
    printWaypoints(waypoints);
    
    // Ask for initial position
    std::cout << "Enter initial drone position (x y z): ";
    Vec3 initial_pos = inputWaypoint(0);
    
    // Setup logging
    bool enable_logging = askYesNo("\nDo you want to save trajectory data to CSV?");
    std::unique_ptr<TrajectoryLogger> logger;
    if (enable_logging) {
        logger = std::make_unique<TrajectoryLogger>("trajectory_output.csv");
        if (!logger->isOpen()) {
            std::cout << "Warning: Could not create CSV file. Continuing without logging." << std::endl;
            logger.reset();
        }
    }
    
    // Ask for detailed output
    bool detailed_output = askYesNo("Do you want detailed console output for every step?");
    
    // Initialize state
    DroneState current_state;
    current_state.position = initial_pos;
    current_state.velocity = Vec3(0, 0, 0);
    current_state.acceleration = Vec3(0, 0, 0);
    current_state.timestamp = 0.0;
    
    std::cout << "\n=== Starting Simulation ===" << std::endl;
    printState(current_state, "Initial State");
    
    // Determine which prediction method to use
    bool use_ml = (predictor != nullptr && predictor->isReady());
    PhysicsTrajectoryGenerator physics_gen;
    
    if (use_ml) {
        std::cout << "\nUsing ML-based trajectory prediction" << std::endl;
    } else {
        std::cout << "\nUsing physics-based trajectory prediction" << std::endl;
        
        // Build history for ML if available
        if (predictor != nullptr) {
            std::cout << "Building state history for ML predictor..." << std::endl;
            for (int i = 0; i < predictor->getSequenceLength(); ++i) {
                predictor->addState(current_state);
                DroneState next_state;
                physics_gen.update(current_state, waypoints[0], 0.1f, next_state);
                current_state = next_state;
            }
            use_ml = true;
            std::cout << "ML predictor ready!\n" << std::endl;
        }
    }
    
    if (detailed_output) {
        std::cout << "\n=== Trajectory Data Points ===" << std::endl;
        std::cout << std::string(120, '-') << std::endl;
    }
    
    // Simulate trajectory
    size_t current_waypoint_idx = 0;
    Vec3 target = waypoints[current_waypoint_idx];
    int step = 0;
    int max_steps = 1000;
    float dt = 0.1f;
    
    while (step < max_steps && current_waypoint_idx < waypoints.size()) {
        // Check if reached current waypoint
        Vec3 to_target = target - current_state.position;
        float dist = to_target.norm();
        
        if (dist < 0.5f) {
            std::cout << "\n✓ Reached waypoint " << (current_waypoint_idx + 1) 
                     << " at t=" << current_state.timestamp << "s" << std::endl;
            
            current_waypoint_idx++;
            if (current_waypoint_idx >= waypoints.size()) {
                std::cout << "\n✓✓✓ All waypoints reached! ✓✓✓" << std::endl;
                break;
            }
            
            target = waypoints[current_waypoint_idx];
            std::cout << "→ Moving to waypoint " << (current_waypoint_idx + 1) 
                     << ": (" << target.x << ", " << target.y << ", " 
                     << target.z << ")\n" << std::endl;
        }
        
        // Log current state
        if (logger) {
            logger->log(step, current_state, target);
        }
        
        // Print detailed output
        if (detailed_output) {
            printDetailedState(current_state, step, target);
        } else if (step % 10 == 0) {
            // Print summary every 10 steps
            std::cout << "Step " << step << " | t=" << std::fixed << std::setprecision(2)
                     << current_state.timestamp << "s | Distance: " 
                     << dist << "m | Waypoint " << (current_waypoint_idx + 1) 
                     << "/" << waypoints.size() << std::endl;
        }
        
        // Predict/compute next state
        DroneState next_state;
        if (use_ml) {
            if (predictor->predict(target, next_state)) {
                current_state = next_state;
                predictor->addState(current_state);
            } else {
                std::cerr << "Prediction failed at step " << step << std::endl;
                break;
            }
        } else {
            physics_gen.update(current_state, target, dt, next_state);
            current_state = next_state;
        }
        
        step++;
    }
    
    if (detailed_output) {
        std::cout << std::string(120, '-') << std::endl;
    }
    
    // Print final statistics
    std::cout << "\n=== Simulation Complete ===" << std::endl;
    std::cout << "Total steps: " << step << std::endl;
    std::cout << "Total time: " << current_state.timestamp << " seconds" << std::endl;
    std::cout << "Waypoints reached: " << current_waypoint_idx << "/" << waypoints.size() << std::endl;
    printState(current_state, "\nFinal State");
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
    std::cout << "╔═══════════════════════════════════════════════╗" << std::endl;
    std::cout << "║  Drone Trajectory Prediction - C++ Demo     ║" << std::endl;
    std::cout << "║  Dynamic Waypoint Input with Model Output   ║" << std::endl;
    std::cout << "╚═══════════════════════════════════════════════╝" << std::endl;
    std::cout << std::endl;
    
    // Paths to model files
    std::string model_path = "../models/drone_trajectory.onnx";
    std::string norm_path = "../models/drone_trajectory_normalization.txt";
    
    // Check if model files exist
    bool ml_available = true;
    std::ifstream model_file(model_path);
    std::ifstream norm_file(norm_path);
    
    if (!model_file.good() || !norm_file.good()) {
        std::cout << "⚠ Warning: ML model files not found." << std::endl;
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
    
    // Display menu
    std::cout << "\n=== Select Mode ===" << std::endl;
    std::cout << "1. Interactive Mode (Dynamic Waypoint Input)" << std::endl;
    std::cout << "2. Demo Mode (Predefined Waypoints)" << std::endl;
    std::cout << "3. Benchmark Mode" << std::endl;
    std::cout << "4. Exit" << std::endl;
    std::cout << "\nEnter your choice (1-4): ";
    
    int choice;
    if (!(std::cin >> choice)) {
        std::cout << "Invalid input. Exiting." << std::endl;
        return 1;
    }
    
    switch (choice) {
        case 1: {
            // Interactive Mode - Main feature requested
            TrajectoryPredictor* predictor_ptr = nullptr;
            std::unique_ptr<TrajectoryPredictor> predictor;
            
            if (ml_available) {
                predictor = std::make_unique<TrajectoryPredictor>(model_path, norm_path, 10);
                if (predictor->initialize()) {
                    predictor_ptr = predictor.get();
                    std::cout << "✓ ML model loaded successfully!" << std::endl;
                } else {
                    std::cout << "⚠ Failed to load ML model. Using physics-based prediction." << std::endl;
                }
            }
            
            runInteractiveTrajectory(predictor_ptr);
            break;
        }
        
        case 2: {
            // Demo Mode
            if (ml_available) {
                runMLPrediction(model_path, norm_path);
            }
            runPhysicsPrediction();
            break;
        }
        
        case 3: {
            // Benchmark Mode
            if (ml_available) {
                performanceBenchmark(model_path, norm_path);
            } else {
                std::cout << "Benchmark requires ML model. Please train the model first." << std::endl;
            }
            break;
        }
        
        case 4: {
            std::cout << "Exiting. Goodbye!" << std::endl;
            return 0;
        }
        
        default: {
            std::cout << "Invalid choice. Exiting." << std::endl;
            return 1;
        }
    }
    
    std::cout << "\n✓ Demo complete!" << std::endl;
    
    return 0;
}
