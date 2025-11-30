# Windows Build Instructions

## The Problem

On Windows, CMake generates **Visual Studio project files** by default, not Makefiles. This means the `make` command won't work. You'll see this error:

```
'make' is not recognized as an internal or external command,
operable program or batch file.
```

## Solutions

### Option 1: Use the Build Scripts (Easiest)

We've provided two build scripts for Windows:

#### Using Batch File
```batch
cd cpp
build_windows.bat
```

#### Using PowerShell
```powershell
cd cpp
.\build_windows.ps1
```

Both scripts will:
1. Create the build directory
2. Run CMake configuration
3. Build the project in Release mode
4. Show the executable location
5. Optionally run the executable

### Option 2: Manual Build with CMake (Cross-Platform)

If you prefer to build manually:

```batch
cd cpp
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

The executable will be in: `build\Release\drone_trajectory_cpp.exe`

### Option 3: Use Visual Studio IDE

After running CMake configuration:

```batch
cd cpp
mkdir build
cd build
cmake ..
```

1. Open `build\DroneTrajectory.sln` in Visual Studio
2. Set build configuration to "Release" (or "Debug")
3. Press F7 or Build → Build Solution
4. Run with F5 or Debug → Start Debugging

### Option 4: Use Ninja Generator (Advanced)

If you have Ninja installed, you can use it instead of Visual Studio:

```batch
cd cpp
mkdir build
cd build
cmake -G Ninja ..
ninja
```

This allows you to use `ninja` instead of `make`, and it works similarly.

## Common Issues

### Issue: "CMake not found"
**Solution**: Install CMake from https://cmake.org/download/ and add it to PATH

### Issue: "Visual Studio not found"
**Solution**: Install Visual Studio 2022 (Community Edition is free) with C++ development tools

### Issue: "ONNX Runtime not found"
**Solution**: Make sure you have ONNX Runtime installed. See the main README for instructions.

### Issue: "Permission denied" when running PowerShell script
**Solution**: Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Quick Reference

| Task | Command |
|------|---------|
| Build (Batch) | `build_windows.bat` |
| Build (PowerShell) | `.\build_windows.ps1` |
| Build (Manual) | `cmake --build build --config Release` |
| Clean build | Delete `build` folder and rebuild |
| Debug build | `cmake --build build --config Debug` |
| Run executable | `build\Release\drone_trajectory_cpp.exe` |

## Build Configurations

CMake supports multiple build configurations:

- **Release**: Optimized, no debug info (recommended for production)
- **Debug**: Debug symbols, no optimization (for development)
- **RelWithDebInfo**: Optimized with debug info
- **MinSizeRel**: Optimized for size

To build with a specific configuration:
```batch
cmake --build build --config Debug
```

## Tips

1. **First time building?** Use the provided batch or PowerShell script - they handle everything for you.

2. **Rebuilding?** Just run the build script again - it will detect existing build files and rebuild only what changed.

3. **Clean build needed?** Delete the `build` folder and run the build script again:
   ```batch
   rmdir /s /q build
   build_windows.bat
   ```

4. **Want to see verbose output?** Add `--verbose` flag:
   ```batch
   cmake --build build --config Release --verbose
   ```

5. **Parallel builds**: CMake automatically uses multiple cores with Visual Studio generator.

## Additional Resources

- [CMake Documentation](https://cmake.org/documentation/)
- [Visual Studio C++ Documentation](https://docs.microsoft.com/en-us/cpp/)
- [ONNX Runtime Documentation](https://onnxruntime.ai/docs/)
