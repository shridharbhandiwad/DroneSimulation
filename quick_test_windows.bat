@echo off
REM Quick Test Script for Windows
REM Tests Python installation and runs a simple demo without full training

echo ==========================================
echo Drone Trajectory - Quick Test (Windows)
echo ==========================================
echo.
echo This script runs a quick test without training.
echo For full demo with training, use run_demo.bat
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [31mError: Python not found[0m
    exit /b 1
)

echo [32m✓[0m Python found
echo.

REM Test Python imports
echo Testing Python packages...
python -c "import numpy; print('  ✓ NumPy')" 2>nul || echo [33m  ✗ NumPy not installed[0m
python -c "import torch; print('  ✓ PyTorch')" 2>nul || echo [33m  ✗ PyTorch not installed[0m
python -c "import PyQt5; print('  ✓ PyQt5')" 2>nul || echo [33m  ✗ PyQt5 not installed[0m
python -c "import onnxruntime; print('  ✓ ONNX Runtime')" 2>nul || echo [33m  ✗ ONNX Runtime not installed[0m

echo.
echo If any packages are missing, run: pip install -r requirements.txt
echo.

REM Quick test script
echo Running quick Python test...
cd python

python -c "from trajectory_generator import DroneTrajectoryGenerator; import numpy as np; gen = DroneTrajectoryGenerator(); waypoints = np.array([[0, 0, 0], [10, 10, 5], [20, 0, 10]]); traj = gen.generate_trajectory(waypoints); print('✓ Trajectory generation works!'); print(f'  Generated {len(traj)} trajectory points')"

if errorlevel 1 (
    echo [31mTest failed![0m
    exit /b 1
)

cd ..

echo.
echo ==========================================
echo Quick test passed!
echo ==========================================
echo.
echo Next steps:
echo   1. Run full demo:       run_demo.bat
echo   2. Run simulation:      cd python ^&^& python simulation.py
echo   3. See documentation:   QUICKSTART_WINDOWS.md
echo.
pause
