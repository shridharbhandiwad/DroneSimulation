@echo off
REM Windows Build Script for Drone Trajectory C++ Project
REM This script builds the project using CMake and Visual Studio

echo ========================================
echo Building Drone Trajectory C++ Project
echo ========================================
echo.

REM Create build directory if it doesn't exist
if not exist build (
    echo Creating build directory...
    mkdir build
)

REM Navigate to build directory
cd build

REM Run CMake to generate Visual Studio project files
echo.
echo Running CMake configuration...
cmake ..
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: CMake configuration failed!
    cd ..
    pause
    exit /b %ERRORLEVEL%
)

REM Build the project using CMake (works with any generator)
echo.
echo Building project...
cmake --build . --config Release
if %ERRORLEVEL% neq 0 (
    echo.
    echo ERROR: Build failed!
    cd ..
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: build\Release\drone_trajectory_cpp.exe
echo.

cd ..

REM Ask if user wants to run the executable
echo Do you want to run the executable now? (Y/N)
choice /c YN /n
if %ERRORLEVEL% equ 1 (
    echo.
    echo Running executable...
    echo.
    build\Release\drone_trajectory_cpp.exe
)

pause
