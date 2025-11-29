@echo off
REM Drone Trajectory Demo Script for Windows
REM This script runs the complete pipeline from data generation to C++ inference

setlocal EnableDelayedExpansion

echo ==========================================
echo Drone Trajectory System - Complete Demo
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    exit /b 1
)

REM Check if pip packages are installed
echo Checking Python dependencies...
python -c "import torch; import numpy; import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install Python dependencies
        exit /b 1
    )
)

REM Step 1: Generate training data
echo.
echo Step 1: Generating training data...
echo ------------------------------------
cd python

if not exist "..\data\train_data.pkl" (
    python data_generator.py
    if errorlevel 1 (
        echo Error: Failed to generate training data
        exit /b 1
    )
    echo [32m✓[0m Training data generated
) else (
    echo Training data already exists
)

REM Step 2: Train model
echo.
echo Step 2: Training LSTM model...
echo ------------------------------------

if not exist "..\models\best_model.pth" (
    python train_model.py
    if errorlevel 1 (
        echo Error: Failed to train model
        exit /b 1
    )
    echo [32m✓[0m Model trained
) else (
    echo Model already exists
)

REM Step 3: Export to ONNX
echo.
echo Step 3: Exporting to ONNX...
echo ------------------------------------

if not exist "..\models\drone_trajectory.onnx" (
    python export_to_onnx.py
    if errorlevel 1 (
        echo Error: Failed to export model to ONNX
        exit /b 1
    )
    echo [32m✓[0m Model exported to ONNX
) else (
    echo ONNX model already exists
)

REM Step 4: Build C++ code
echo.
echo Step 4: Building C++ code...
echo ------------------------------------
cd ..\cpp

if not exist "build" (
    mkdir build
)

cd build

REM Check if CMake is available
cmake --version >nul 2>&1
if errorlevel 1 (
    echo Warning: CMake is not installed. Skipping C++ build.
    echo Install CMake from https://cmake.org/download/ to build C++ components.
    goto :summary
)

REM Detect Visual Studio - check multiple editions and verify C++ tools
set VS_GENERATOR=

REM Check Visual Studio 2022
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    set VS_GENERATOR=-G "Visual Studio 17 2022" -A x64
    echo Detected Visual Studio 2022 ^(Community edition^)
    goto :vs_found
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat" (
    set VS_GENERATOR=-G "Visual Studio 17 2022" -A x64
    echo Detected Visual Studio 2022 ^(Professional edition^)
    goto :vs_found
)
if exist "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" (
    set VS_GENERATOR=-G "Visual Studio 17 2022" -A x64
    echo Detected Visual Studio 2022 ^(Enterprise edition^)
    goto :vs_found
)

REM Check Visual Studio 2019
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    set VS_GENERATOR=-G "Visual Studio 16 2019" -A x64
    echo Detected Visual Studio 2019 ^(Community edition^)
    goto :vs_found
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Professional\VC\Auxiliary\Build\vcvarsall.bat" (
    set VS_GENERATOR=-G "Visual Studio 16 2019" -A x64
    echo Detected Visual Studio 2019 ^(Professional edition^)
    goto :vs_found
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" (
    set VS_GENERATOR=-G "Visual Studio 16 2019" -A x64
    echo Detected Visual Studio 2019 ^(Enterprise edition^)
    goto :vs_found
)

REM Check Visual Studio 2017
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat" (
    set VS_GENERATOR=-G "Visual Studio 15 2017" -A x64
    echo Detected Visual Studio 2017 ^(Community edition^)
    goto :vs_found
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\VC\Auxiliary\Build\vcvarsall.bat" (
    set VS_GENERATOR=-G "Visual Studio 15 2017" -A x64
    echo Detected Visual Studio 2017 ^(Professional edition^)
    goto :vs_found
)
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Auxiliary\Build\vcvarsall.bat" (
    set VS_GENERATOR=-G "Visual Studio 15 2017" -A x64
    echo Detected Visual Studio 2017 ^(Enterprise edition^)
    goto :vs_found
)

REM No Visual Studio found
echo.
echo [91mWARNING: No Visual Studio installation with C++ tools detected![0m
echo.
echo [93mVisual Studio is required to build C++ components.[0m
echo.
echo [96mSolutions:[0m
echo   1. Install Visual Studio 2022 Community ^(Free^):
echo      https://visualstudio.microsoft.com/downloads/
echo      Make sure to select 'Desktop development with C++' workload
echo.
echo   2. Or use MinGW as an alternative:
echo      See VISUAL_STUDIO_NOT_FOUND_SOLUTION.md for details
echo.
echo [93mSkipping C++ build...[0m
goto :summary

:vs_found

echo Configuring with CMake...
cmake .. %VS_GENERATOR% >nul 2>&1
if errorlevel 1 (
    echo Warning: CMake configuration failed. This is OK if ONNX Runtime is not installed.
    echo See cpp\README_CPP.md for installation instructions.
    goto :summary
)

echo Building...
cmake --build . --config Release >nul 2>&1
if errorlevel 1 (
    echo Warning: C++ build failed. This is OK if ONNX Runtime is not installed.
    echo See cpp\README_CPP.md for installation instructions.
    goto :summary
)

echo [32m✓[0m C++ code built successfully

REM Step 5: Run C++ demo
echo.
echo Step 5: Running C++ demo...
echo ------------------------------------

if exist "Release\drone_trajectory_cpp.exe" (
    Release\drone_trajectory_cpp.exe
) else if exist "drone_trajectory_cpp.exe" (
    drone_trajectory_cpp.exe
) else (
    echo Warning: C++ executable not found
)

:summary
REM Summary
cd ..\..
echo.
echo ==========================================
echo Demo Complete!
echo ==========================================
echo.
echo What was created:
echo   • Training data: data\train_data.pkl
echo   • Trained model: models\best_model.pth
echo   • ONNX model: models\drone_trajectory.onnx
echo   • C++ executable: cpp\build\Release\drone_trajectory_cpp.exe
echo.
echo Next steps:
echo   • Run Python simulation: cd python ^&^& python simulation.py
echo   • Run C++ demo again: cd cpp\build\Release ^&^& drone_trajectory_cpp.exe
echo   • See QUICKSTART_WINDOWS.md for more options
echo.

endlocal
