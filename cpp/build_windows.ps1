# Windows Build Script for Drone Trajectory C++ Project (PowerShell)
# This script builds the project using CMake and Visual Studio

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building Drone Trajectory C++ Project" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Create build directory if it doesn't exist
if (-not (Test-Path "build")) {
    Write-Host "Creating build directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "build" | Out-Null
}

# Navigate to build directory
Set-Location "build"

# Run CMake to generate Visual Studio project files
Write-Host ""
Write-Host "Running CMake configuration..." -ForegroundColor Yellow
cmake ..
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: CMake configuration failed!" -ForegroundColor Red
    Set-Location ".."
    Read-Host "Press Enter to exit"
    exit $LASTEXITCODE
}

# Build the project using CMake (works with any generator)
Write-Host ""
Write-Host "Building project..." -ForegroundColor Yellow
cmake --build . --config Release
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    Set-Location ".."
    Read-Host "Press Enter to exit"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Executable location: build\Release\drone_trajectory_cpp.exe" -ForegroundColor Cyan
Write-Host ""

Set-Location ".."

# Ask if user wants to run the executable
$response = Read-Host "Do you want to run the executable now? (Y/N)"
if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "Running executable..." -ForegroundColor Yellow
    Write-Host ""
    & "build\Release\drone_trajectory_cpp.exe"
}

Read-Host "Press Enter to exit"
