# Drone Trajectory Demo Script for Windows (PowerShell)
# This script runs the complete pipeline from data generation to C++ inference

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Drone Trajectory System - Complete Demo" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

# Check if pip packages are installed
Write-Host "Checking Python dependencies..."
$result = python -c "import torch; import numpy; import PyQt5" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install Python dependencies" -ForegroundColor Red
        exit 1
    }
}

# Step 1: Generate training data
Write-Host ""
Write-Host "Step 1: Generating training data..." -ForegroundColor Cyan
Write-Host "------------------------------------"
Push-Location python

if (-not (Test-Path "..\data\train_data.pkl")) {
    python data_generator.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Training data generated" -ForegroundColor Green
    } else {
        Write-Host "Error: Failed to generate training data" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} else {
    Write-Host "Training data already exists" -ForegroundColor Gray
}

# Step 2: Train model
Write-Host ""
Write-Host "Step 2: Training LSTM model..." -ForegroundColor Cyan
Write-Host "------------------------------------"

if (-not (Test-Path "..\models\best_model.pth")) {
    python train_model.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Model trained" -ForegroundColor Green
    } else {
        Write-Host "Error: Failed to train model" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} else {
    Write-Host "Model already exists" -ForegroundColor Gray
}

# Step 3: Export to ONNX
Write-Host ""
Write-Host "Step 3: Exporting to ONNX..." -ForegroundColor Cyan
Write-Host "------------------------------------"

if (-not (Test-Path "..\models\drone_trajectory.onnx")) {
    python export_to_onnx.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Model exported to ONNX" -ForegroundColor Green
    } else {
        Write-Host "Error: Failed to export model to ONNX" -ForegroundColor Red
        Pop-Location
        exit 1
    }
} else {
    Write-Host "ONNX model already exists" -ForegroundColor Gray
}

Pop-Location

# Step 4: Build C++ code
Write-Host ""
Write-Host "Step 4: Building C++ code..." -ForegroundColor Cyan
Write-Host "------------------------------------"
Push-Location cpp

if (-not (Test-Path "build")) {
    New-Item -ItemType Directory -Path "build" | Out-Null
}

Push-Location build

# Check if CMake is available
try {
    $cmakeVersion = cmake --version 2>&1 | Select-String -Pattern "cmake version"
    Write-Host "Found: $cmakeVersion" -ForegroundColor Green
} catch {
    Write-Host "Warning: CMake is not installed. Skipping C++ build." -ForegroundColor Yellow
    Write-Host "Install CMake from https://cmake.org/download/ to build C++ components." -ForegroundColor Yellow
    Pop-Location
    Pop-Location
    $buildSuccess = $false
}

if ($buildSuccess -ne $false) {
    # Detect Visual Studio
    $vsGenerator = ""
    if (Test-Path "C:\Program Files\Microsoft Visual Studio\2022") {
        $vsGenerator = "-G `"Visual Studio 17 2022`" -A x64"
        Write-Host "Detected Visual Studio 2022" -ForegroundColor Green
    } elseif (Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\2019") {
        $vsGenerator = "-G `"Visual Studio 16 2019`" -A x64"
        Write-Host "Detected Visual Studio 2019" -ForegroundColor Green
    } elseif (Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\2017") {
        $vsGenerator = "-G `"Visual Studio 15 2017`" -A x64"
        Write-Host "Detected Visual Studio 2017" -ForegroundColor Green
    } else {
        Write-Host "No Visual Studio detected, trying default generator..." -ForegroundColor Yellow
    }

    Write-Host "Configuring with CMake..."
    if ($vsGenerator -ne "") {
        $cmakeCmd = "cmake .. $vsGenerator"
        Invoke-Expression $cmakeCmd 2>&1 | Out-Null
    } else {
        cmake .. 2>&1 | Out-Null
    }

    if ($LASTEXITCODE -ne 0) {
        Write-Host "Warning: CMake configuration failed." -ForegroundColor Yellow
        Write-Host "This is OK if ONNX Runtime is not installed." -ForegroundColor Yellow
        Write-Host "See cpp\README_CPP.md for installation instructions." -ForegroundColor Yellow
        Pop-Location
        Pop-Location
        $buildSuccess = $false
    } else {
        Write-Host "Building..."
        cmake --build . --config Release 2>&1 | Out-Null
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Warning: C++ build failed." -ForegroundColor Yellow
            Write-Host "This is OK if ONNX Runtime is not installed." -ForegroundColor Yellow
            Write-Host "See cpp\README_CPP.md for installation instructions." -ForegroundColor Yellow
            Pop-Location
            Pop-Location
            $buildSuccess = $false
        } else {
            Write-Host "✓ C++ code built successfully" -ForegroundColor Green
            
            # Step 5: Run C++ demo
            Write-Host ""
            Write-Host "Step 5: Running C++ demo..." -ForegroundColor Cyan
            Write-Host "------------------------------------"
            
            if (Test-Path "Release\drone_trajectory_cpp.exe") {
                .\Release\drone_trajectory_cpp.exe
            } elseif (Test-Path "drone_trajectory_cpp.exe") {
                .\drone_trajectory_cpp.exe
            } else {
                Write-Host "Warning: C++ executable not found" -ForegroundColor Yellow
            }
            
            Pop-Location
            Pop-Location
        }
    }
}

# Summary
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Demo Complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "What was created:"
Write-Host "  • Training data: data\train_data.pkl" -ForegroundColor White
Write-Host "  • Trained model: models\best_model.pth" -ForegroundColor White
Write-Host "  • ONNX model: models\drone_trajectory.onnx" -ForegroundColor White
Write-Host "  • C++ executable: cpp\build\Release\drone_trajectory_cpp.exe" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  • Run Python simulation: cd python; python simulation.py"
Write-Host "  • Run C++ demo again: cd cpp\build\Release; .\drone_trajectory_cpp.exe"
Write-Host "  • See QUICKSTART_WINDOWS.md for more options"
Write-Host ""
