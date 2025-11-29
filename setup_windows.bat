@echo off
REM Windows Setup Script for Drone Trajectory System
REM This script installs dependencies and configures the environment

setlocal EnableDelayedExpansion

echo ==========================================
echo Drone Trajectory System - Windows Setup
echo ==========================================
echo.

REM Check Python installation
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [31mError: Python is not installed or not in PATH[0m
    echo.
    echo Please install Python 3.8 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [32m✓[0m Python !PYTHON_VERSION! found
)

REM Check pip
echo [2/5] Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [31mError: pip is not installed[0m
    echo Installing pip...
    python -m ensurepip --default-pip
    if errorlevel 1 (
        echo [31mFailed to install pip[0m
        exit /b 1
    )
) else (
    echo [32m✓[0m pip is available
)

REM Upgrade pip
echo Upgrading pip to latest version...
python -m pip install --upgrade pip >nul 2>&1

REM Install Python dependencies
echo [3/5] Installing Python dependencies...
echo This may take a few minutes...
echo.

if not exist "requirements.txt" (
    echo [31mError: requirements.txt not found[0m
    echo Please run this script from the project root directory.
    exit /b 1
)

pip install -r requirements.txt
if errorlevel 1 (
    echo [31mError: Failed to install Python dependencies[0m
    echo.
    echo Try running manually:
    echo   pip install -r requirements.txt
    exit /b 1
)

echo [32m✓[0m Python dependencies installed successfully

REM Create necessary directories
echo [4/5] Creating project directories...
if not exist "data" mkdir data
if not exist "models" mkdir models
if not exist "cpp\build" mkdir cpp\build
echo [32m✓[0m Directories created

REM Check optional dependencies
echo [5/5] Checking optional dependencies...
echo.

REM Check CMake
cmake --version >nul 2>&1
if errorlevel 1 (
    echo [33m⚠[0m CMake is not installed (optional for C++ build)
    echo   Download from: https://cmake.org/download/
    set HAS_CMAKE=0
) else (
    for /f "tokens=3" %%i in ('cmake --version 2^>^&1 ^| findstr /C:"cmake version"') do set CMAKE_VERSION=%%i
    echo [32m✓[0m CMake !CMAKE_VERSION! found
    set HAS_CMAKE=1
)

REM Check Visual Studio
set VS_FOUND=0
if exist "C:\Program Files\Microsoft Visual Studio\2022" (
    echo [32m✓[0m Visual Studio 2022 found
    set VS_FOUND=1
    set VS_VERSION=2022
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019" (
    echo [32m✓[0m Visual Studio 2019 found
    set VS_FOUND=1
    set VS_VERSION=2019
) else if exist "C:\Program Files (x86)\Microsoft Visual Studio\2017" (
    echo [32m✓[0m Visual Studio 2017 found
    set VS_FOUND=1
    set VS_VERSION=2017
) else (
    echo [33m⚠[0m Visual Studio is not installed (optional for C++ build)
    echo   Download from: https://visualstudio.microsoft.com/downloads/
    echo   Install "Desktop development with C++" workload
    set VS_FOUND=0
)

REM Check for CUDA (optional, for GPU acceleration)
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo [33m⚠[0m NVIDIA GPU not detected or drivers not installed
    echo   Training will use CPU (slower but still works)
    set HAS_CUDA=0
) else (
    echo [32m✓[0m NVIDIA GPU detected
    echo   PyTorch will use CUDA for faster training
    set HAS_CUDA=1
)

REM Summary
echo.
echo ==========================================
echo Setup Complete!
echo ==========================================
echo.
echo Installation Summary:
echo   [32m✓[0m Python !PYTHON_VERSION!
echo   [32m✓[0m Python packages installed
echo   [32m✓[0m Project directories created

if !HAS_CMAKE! EQU 1 (
    echo   [32m✓[0m CMake available
) else (
    echo   [33m⚠[0m CMake not available
)

if !VS_FOUND! EQU 1 (
    echo   [32m✓[0m Visual Studio !VS_VERSION! available
) else (
    echo   [33m⚠[0m Visual Studio not available
)

if !HAS_CUDA! EQU 1 (
    echo   [32m✓[0m CUDA GPU available
) else (
    echo   [33m⚠[0m CUDA GPU not available - will use CPU
)

echo.
echo Next Steps:
echo ==========================================
echo.
echo To run the complete demo pipeline:
echo   run_demo.bat
echo.
echo Or run steps individually:
echo   1. Generate training data:
echo      cd python ^&^& python data_generator.py
echo.
echo   2. Train the model:
echo      python train_model.py
echo.
echo   3. Run simulation:
echo      python simulation.py
echo.
echo   4. Export to ONNX:
echo      python export_to_onnx.py
echo.

if !HAS_CMAKE! EQU 1 (
    if !VS_FOUND! EQU 1 (
        echo   5. Build C++ code:
        echo      cd ..\cpp\build
        echo      cmake .. -G "Visual Studio 17 2022" -A x64
        echo      cmake --build . --config Release
        echo.
    )
)

echo For more information, see:
echo   - README.md (General documentation)
echo   - QUICKSTART_WINDOWS.md (Windows-specific guide)
echo   - QUICKSTART.md (General quickstart)
echo.

REM Test imports
echo Testing Python imports...
python -c "import torch; import numpy; import PyQt5; print('All imports successful!')" 2>nul
if errorlevel 1 (
    echo [33m⚠[0m Warning: Some Python packages may not have been installed correctly
    echo Try reinstalling: pip install -r requirements.txt
) else (
    echo [32m✓[0m All Python imports successful
)

echo.
echo Setup completed successfully!
echo Press any key to exit...
pause >nul

endlocal
