#!/bin/bash

# Drone Trajectory Demo Script
# This script runs the complete pipeline from data generation to C++ inference

set -e  # Exit on error

echo "=========================================="
echo "Drone Trajectory System - Complete Demo"
echo "=========================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if pip packages are installed
echo "Checking Python dependencies..."
python3 -c "import torch; import numpy; import PyQt5" 2>/dev/null || {
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
}

# Step 1: Generate training data
echo ""
echo "Step 1: Generating training data..."
echo "------------------------------------"
cd python

if [ ! -f "../data/train_data.pkl" ]; then
    python3 data_generator.py
    echo "✓ Training data generated"
else
    echo "Training data already exists (skip with --force to regenerate)"
fi

# Step 2: Train model
echo ""
echo "Step 2: Training LSTM model..."
echo "------------------------------------"

if [ ! -f "../models/best_model.pth" ]; then
    python3 train_model.py
    echo "✓ Model trained"
else
    echo "Model already exists (skip with --force to retrain)"
fi

# Step 3: Export to ONNX
echo ""
echo "Step 3: Exporting to ONNX..."
echo "------------------------------------"

if [ ! -f "../models/drone_trajectory.onnx" ]; then
    python3 export_to_onnx.py
    echo "✓ Model exported to ONNX"
else
    echo "ONNX model already exists"
fi

# Step 4: Build C++ code
echo ""
echo "Step 4: Building C++ code..."
echo "------------------------------------"
cd ../cpp

if [ ! -d "build" ]; then
    mkdir build
fi

cd build

# Check if CMake is available
if ! command -v cmake &> /dev/null; then
    echo "Warning: CMake is not installed. Skipping C++ build."
    echo "Install CMake to build C++ components."
else
    cmake .. 2>&1 | grep -E "(ONNX|Build|--)" || true
    
    if make -j4 2>&1 | grep -E "(error|Error)" ; then
        echo "Warning: C++ build failed. This is OK if ONNX Runtime is not installed."
        echo "See cpp/README_CPP.md for installation instructions."
    else
        echo "✓ C++ code built successfully"
        
        # Step 5: Run C++ demo
        echo ""
        echo "Step 5: Running C++ demo..."
        echo "------------------------------------"
        ./drone_trajectory_cpp
    fi
fi

# Summary
echo ""
echo "=========================================="
echo "Demo Complete!"
echo "=========================================="
echo ""
echo "What was created:"
echo "  • Training data: data/train_data.pkl"
echo "  • Trained model: models/best_model.pth"
echo "  • ONNX model: models/drone_trajectory.onnx"
echo "  • C++ executable: cpp/build/drone_trajectory_cpp"
echo ""
echo "Next steps:"
echo "  • Run Python simulation: cd python && python3 simulation.py"
echo "  • Run C++ demo again: cd cpp/build && ./drone_trajectory_cpp"
echo "  • See QUICKSTART.md for more options"
echo ""
