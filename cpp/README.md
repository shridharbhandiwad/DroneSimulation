# Drone Trajectory C++ Implementation

This directory contains the C++ implementation of the drone trajectory prediction system using ONNX Runtime.

## Quick Start

### Windows Users

**The easiest way to build on Windows:**

```batch
cd cpp
build_windows.bat
```

Or using PowerShell:
```powershell
cd cpp
.\build_windows.ps1
```

**Important**: Don't use `make` on Windows! CMake generates Visual Studio project files by default, not Makefiles. See [BUILD_INSTRUCTIONS_WINDOWS.md](BUILD_INSTRUCTIONS_WINDOWS.md) for detailed instructions.

### Linux/Mac Users

```bash
cd cpp
mkdir -p build && cd build
cmake ..
make
./drone_trajectory_cpp
```

## Files

- `drone_trajectory.h` - Header file with the DroneTrajectory class interface
- `drone_trajectory.cpp` - Implementation of trajectory prediction using ONNX
- `main.cpp` - Example usage and demo
- `CMakeLists.txt` - CMake build configuration
- `build_windows.bat` - Windows build script (Batch)
- `build_windows.ps1` - Windows build script (PowerShell)
- `BUILD_INSTRUCTIONS_WINDOWS.md` - Detailed Windows build instructions

## Requirements

- CMake 3.15 or higher
- C++17 compatible compiler
  - Windows: Visual Studio 2019/2022 with C++ tools
  - Linux: GCC 7+ or Clang 5+
  - Mac: Xcode 10+
- ONNX Runtime 1.17.1 (or compatible version)

## Building

### Windows

See [BUILD_INSTRUCTIONS_WINDOWS.md](BUILD_INSTRUCTIONS_WINDOWS.md) for multiple options including:
- Using the provided build scripts (easiest)
- Manual CMake commands
- Building in Visual Studio IDE
- Using Ninja generator

### Linux/Mac

```bash
# Create build directory
mkdir -p build && cd build

# Configure
cmake ..

# Build
make

# Run
./drone_trajectory_cpp
```

### Custom ONNX Runtime Location

If ONNX Runtime is not found automatically, specify the location:

```bash
cmake -DONNXRUNTIME_DIR=/path/to/onnxruntime ..
```

On Windows:
```batch
cmake -DONNXRUNTIME_DIR="C:/path/to/onnxruntime" ..
```

## Usage

The executable demonstrates interactive waypoint input and trajectory prediction:

```bash
./drone_trajectory_cpp  # Linux/Mac
build\Release\drone_trajectory_cpp.exe  # Windows
```

Follow the prompts to:
1. Enter target waypoints (position and time)
2. View predicted trajectory
3. See control outputs and estimated arrival times

## Integration

To use the DroneTrajectory class in your own project:

```cpp
#include "drone_trajectory.h"

// Create predictor
DroneTrajectory predictor("path/to/model.onnx");

// Prepare inputs
std::vector<float> target_position = {10.0f, 5.0f, 3.0f};
std::vector<float> current_state = {0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f};
float time_step = 1.0f;

// Predict
auto result = predictor.predict(target_position, current_state, time_step);

// Use results
std::cout << "Control: [" 
          << result.control_output[0] << ", "
          << result.control_output[1] << ", "
          << result.control_output[2] << "]" << std::endl;
```

## Troubleshooting

### Windows: "make is not recognized"

This is expected on Windows. Use one of these alternatives:
- Run `build_windows.bat` or `build_windows.ps1`
- Use `cmake --build . --config Release`
- Open the generated `.sln` file in Visual Studio

See [BUILD_INSTRUCTIONS_WINDOWS.md](BUILD_INSTRUCTIONS_WINDOWS.md) for details.

### "ONNX Runtime not found"

1. Make sure ONNX Runtime is installed
2. Place it in the parent directory: `../onnxruntime-win-x64-1.17.1/`
3. Or specify the path: `cmake -DONNXRUNTIME_DIR=/path/to/onnxruntime ..`

### "Cannot open model file"

Make sure the ONNX model file exists. Generate it from Python:

```bash
cd ../python
python export_to_onnx.py
```

This creates `trajectory_model.onnx` which the C++ program can load.

### Windows: DLL not found when running

The build system automatically copies `onnxruntime.dll` to the executable directory. If you still see this error:

1. Check that `onnxruntime.dll` is in the same folder as the executable
2. Or add the ONNX Runtime lib folder to your PATH

## Documentation

- [BUILD_INSTRUCTIONS_WINDOWS.md](BUILD_INSTRUCTIONS_WINDOWS.md) - Detailed Windows build guide
- [../COMPLETE_TECHNICAL_DOCUMENTATION.md](../COMPLETE_TECHNICAL_DOCUMENTATION.md) - Full technical documentation
- [../README.md](../README.md) - Main project README

## License

See [LICENSE](../LICENSE) in the root directory.
