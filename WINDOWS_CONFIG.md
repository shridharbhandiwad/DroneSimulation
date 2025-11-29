# Windows Configuration Guide

This document provides comprehensive Windows-specific configuration details for the Drone Trajectory Generation and Simulation System.

## Overview

The application has been fully configured for Windows platform with the following enhancements:

### Created Files

1. **run_demo.bat** - Windows batch script for automated demo
2. **run_demo.ps1** - PowerShell script with enhanced output and error handling
3. **setup_windows.bat** - One-time setup script to install dependencies
4. **QUICKSTART_WINDOWS.md** - Comprehensive Windows user guide
5. **Updated CMakeLists.txt** - Enhanced with Windows/MSVC support
6. **Updated .gitignore** - Added Windows-specific exclusions

### Key Features for Windows

- ✅ Visual Studio 2017/2019/2022 support
- ✅ Automatic DLL copying for ONNX Runtime
- ✅ CMake generator auto-detection
- ✅ Both cmd.exe and PowerShell scripts
- ✅ Colored console output (where supported)
- ✅ Comprehensive error handling and troubleshooting
- ✅ Path-aware (handles spaces in paths)
- ✅ Windows-specific dependency checks

## File Descriptions

### 1. run_demo.bat

**Purpose:** Automated demo script for Windows Command Prompt (cmd.exe)

**Features:**
- Checks Python installation and version
- Installs Python dependencies automatically
- Creates necessary directories
- Runs complete pipeline: data generation → training → export → C++ build
- Detects Visual Studio version automatically
- Provides colored output for success/warning/error
- Handles errors gracefully with informative messages

**Usage:**
```batch
run_demo.bat
```

### 2. run_demo.ps1

**Purpose:** PowerShell script with enhanced features

**Features:**
- Modern PowerShell syntax and cmdlets
- Better error handling with try/catch blocks
- Colored output using Write-Host with colors
- Uses PowerShell-native path handling
- More informative status messages
- Better integration with Windows Terminal

**Usage:**
```powershell
.\run_demo.ps1
```

**Note:** You may need to adjust execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. setup_windows.bat

**Purpose:** One-time setup and environment validation

**Features:**
- Validates Python installation
- Checks for pip and upgrades it
- Installs all Python dependencies
- Creates project directories
- Checks for optional dependencies (CMake, Visual Studio, CUDA)
- Provides comprehensive system report
- Tests Python imports to verify installation
- Gives next-step instructions

**Usage:**
```batch
setup_windows.bat
```

**When to use:**
- First time setting up the project
- After cloning the repository
- When dependencies need to be reinstalled
- To verify system configuration

### 4. QUICKSTART_WINDOWS.md

**Purpose:** Comprehensive Windows user documentation

**Content:**
- Step-by-step installation instructions
- Prerequisites and system requirements
- Troubleshooting guide for common Windows issues
- ONNX Runtime installation guide (multiple methods)
- Visual Studio configuration
- Performance expectations on Windows
- Windows-specific tips and tricks
- Path handling and execution policy information

### 5. Updated CMakeLists.txt

**Windows Enhancements:**

#### Additional Search Paths
```cmake
if(WIN32)
    list(APPEND ONNX_SEARCH_PATHS
        "$ENV{ProgramFiles}/onnxruntime"
        "C:/Program Files/onnxruntime"
        "C:/onnxruntime"
        "${CMAKE_SOURCE_DIR}/../onnxruntime"
    )
endif()
```

#### Library Name Handling
```cmake
find_library(ONNXRUNTIME_LIBRARY
    NAMES onnxruntime onnxruntime.lib  # Added .lib for Windows
    ...
)
```

#### Automatic DLL Copying
```cmake
if(WIN32 AND ONNXRUNTIME_DLL)
    add_custom_command(TARGET drone_trajectory_cpp POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            ${ONNXRUNTIME_DLL}
            $<TARGET_FILE_DIR:drone_trajectory_cpp>
    )
endif()
```

#### Platform Information
```cmake
message(STATUS "  Platform: ${CMAKE_SYSTEM_NAME}")
if(WIN32)
    message(STATUS "  Generator: ${CMAKE_GENERATOR}")
endif()
```

### 6. Updated .gitignore

**Added Windows-Specific Entries:**

#### Visual Studio Files
```gitignore
.vs/
*.user
*.suo
*.sln
*.vcxproj
*.vcxproj.filters
*.VC.db
*.opensdf
```

#### Windows Build Artifacts
```gitignore
*.lib
*.dll
*.exp
*.ilk
*.pdb
Debug/
Release/
x64/
Win32/
```

#### Windows System Files
```gitignore
Desktop.ini
$RECYCLE.BIN/
Thumbs.db
ehthumbs.db
*.lnk
```

## Build System Configuration

### Visual Studio Detection

The scripts automatically detect installed Visual Studio versions:

```batch
if exist "C:\Program Files\Microsoft Visual Studio\2022" (
    set VS_GENERATOR=-G "Visual Studio 17 2022" -A x64
)
```

Supported versions:
- Visual Studio 2022 (Generator: "Visual Studio 17 2022")
- Visual Studio 2019 (Generator: "Visual Studio 16 2019")
- Visual Studio 2017 (Generator: "Visual Studio 15 2017")

### CMake Configuration

**Recommended CMake command:**
```batch
cmake .. -G "Visual Studio 17 2022" -A x64 -DONNXRUNTIME_DIR=C:\onnxruntime
```

**Options:**
- `-G` : Specifies generator (Visual Studio version)
- `-A` : Architecture (x64 for 64-bit)
- `-DONNXRUNTIME_DIR` : Path to ONNX Runtime installation

### Build Output Locations

**Debug build:**
```
cpp/build/Debug/drone_trajectory_cpp.exe
cpp/build/Debug/onnxruntime.dll
```

**Release build:**
```
cpp/build/Release/drone_trajectory_cpp.exe
cpp/build/Release/onnxruntime.dll
```

## Python Environment

### Recommended Setup

1. **Python Version:** 3.8 - 3.11
   - Python 3.10 is recommended for best compatibility
   - Avoid Python 3.12+ (some packages may not be available)

2. **Virtual Environment (Optional but Recommended):**
```batch
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. **GPU Support (Optional):**
   - Install CUDA Toolkit from NVIDIA
   - PyTorch will automatically use GPU if available
   - Check with: `python -c "import torch; print(torch.cuda.is_available())"`

### Common Python Issues on Windows

**Issue:** Python not found
```batch
# Solution: Add Python to PATH or use full path
C:\Python310\python.exe -m pip install -r requirements.txt
```

**Issue:** PyQt5 window not appearing
```batch
# Solution: Reinstall PyQt5
pip uninstall PyQt5
pip install PyQt5
```

**Issue:** Long paths causing errors
```batch
# Solution: Enable long paths in Windows
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

## ONNX Runtime Configuration

### Installation Methods

#### Method 1: Binary Download (Easiest)

1. Go to: https://github.com/microsoft/onnxruntime/releases
2. Download: `onnxruntime-win-x64-[version].zip`
3. Extract to: `C:\onnxruntime`
4. Structure should be:
   ```
   C:\onnxruntime\
   ├── include\
   │   └── onnxruntime_cxx_api.h
   └── lib\
       ├── onnxruntime.lib
       └── onnxruntime.dll
   ```

#### Method 2: vcpkg

```batch
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.\bootstrap-vcpkg.bat
.\vcpkg install onnxruntime:x64-windows
```

Then use with CMake:
```batch
cmake .. -DCMAKE_TOOLCHAIN_FILE=[vcpkg-root]\scripts\buildsystems\vcpkg.cmake
```

#### Method 3: NuGet (for Visual Studio)

In Visual Studio:
1. Right-click project → Manage NuGet Packages
2. Search for "Microsoft.ML.OnnxRuntime"
3. Install package

### Verification

Check if ONNX Runtime is properly configured:
```batch
cd cpp\build
cmake .. -G "Visual Studio 17 2022" -A x64 -DONNXRUNTIME_DIR=C:\onnxruntime
```

Look for output:
```
ONNX Runtime include: C:/onnxruntime/include
ONNX Runtime library: C:/onnxruntime/lib/onnxruntime.lib
Found ONNX Runtime DLL: C:/onnxruntime/lib/onnxruntime.dll
```

## Performance Tuning

### Python Performance

**GPU Acceleration:**
- Install CUDA Toolkit (if you have NVIDIA GPU)
- PyTorch with CUDA: ~5x faster training
- Check GPU usage: `nvidia-smi`

**CPU Optimization:**
- Use Release builds for PyTorch
- Increase batch size if you have RAM
- Use multiple workers for data loading

### C++ Performance

**Compiler Optimizations:**
```batch
# Build in Release mode
cmake --build . --config Release

# Or with maximum optimizations
cmake .. -G "Visual Studio 17 2022" -A x64 -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
```

**ONNX Runtime Optimization:**
- Use GPU execution provider if available
- Enable graph optimizations
- Use appropriate number of threads

## Troubleshooting

### Script Issues

**Problem:** Script won't run
```batch
# Solution 1: Check execution policy (PowerShell)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Solution 2: Run as administrator (if needed)
# Right-click → Run as administrator
```

**Problem:** Python not in PATH
```batch
# Solution: Use full path or add to PATH
set PATH=%PATH%;C:\Python310;C:\Python310\Scripts
```

### Build Issues

**Problem:** CMake can't find compiler
```batch
# Solution: Use Developer Command Prompt for VS
# Or specify generator explicitly
cmake .. -G "Visual Studio 17 2022" -A x64
```

**Problem:** Missing onnxruntime.dll
```batch
# Solution: Copy manually
copy C:\onnxruntime\lib\onnxruntime.dll cpp\build\Release\
```

**Problem:** LNK errors (linker errors)
```batch
# Solution: Ensure correct library architecture (x64)
cmake .. -G "Visual Studio 17 2022" -A x64
```

## Best Practices

### Development Workflow

1. **Use Virtual Environment:**
   ```batch
   python -m venv venv
   venv\Scripts\activate
   ```

2. **Regular Updates:**
   ```batch
   pip install --upgrade -r requirements.txt
   ```

3. **Clean Builds:**
   ```batch
   cd cpp\build
   rmdir /s /q *
   cmake .. -G "Visual Studio 17 2022" -A x64
   ```

### Deployment

**Python Application:**
- Use PyInstaller to create standalone .exe
- Include models and data directories
- Test on clean Windows installation

**C++ Application:**
- Build in Release mode
- Include onnxruntime.dll with executable
- Test on target system
- Consider static linking if possible

## System Requirements

### Minimum:
- Windows 10 (64-bit)
- Python 3.8+
- 4 GB RAM
- 2 GB disk space
- Any x64 processor

### Recommended:
- Windows 10/11 (64-bit)
- Python 3.10
- Visual Studio 2022
- 8 GB RAM
- NVIDIA GPU with CUDA
- 5 GB disk space
- Multi-core processor

## Support and Resources

### Documentation
- README.md - Main documentation
- QUICKSTART_WINDOWS.md - User guide
- QUICKSTART.md - General guide
- cpp/README_CPP.md - C++ specific

### External Resources
- [Python Windows Downloads](https://www.python.org/downloads/windows/)
- [Visual Studio Downloads](https://visualstudio.microsoft.com/downloads/)
- [CMake Downloads](https://cmake.org/download/)
- [ONNX Runtime Releases](https://github.com/microsoft/onnxruntime/releases)
- [PyTorch Windows Installation](https://pytorch.org/get-started/locally/)

## Frequently Asked Questions

**Q: Do I need Visual Studio to run the Python code?**
A: No, Visual Studio is only needed for C++ compilation. Python parts work with just Python installed.

**Q: Can I use MinGW instead of Visual Studio?**
A: Yes, but MSVC/Visual Studio is recommended for better compatibility with ONNX Runtime.

**Q: Does it work on Windows 7/8?**
A: Not officially supported. Windows 10+ is required for full functionality.

**Q: Can I run this on Windows ARM?**
A: Not currently. Only x64 (64-bit Intel/AMD) is supported.

**Q: How do I uninstall?**
A: Simply delete the project directory. Python packages can be uninstalled with:
```batch
pip uninstall -r requirements.txt -y
```

## Changelog

### Windows Support - 2025-11-29

**Added:**
- Windows batch script (run_demo.bat)
- PowerShell script (run_demo.ps1)
- Windows setup script (setup_windows.bat)
- Windows quickstart guide (QUICKSTART_WINDOWS.md)
- Windows configuration documentation (this file)

**Updated:**
- CMakeLists.txt with Windows/MSVC support
- .gitignore with Windows-specific patterns
- README.md with Windows sections
- Cross-platform path handling

**Improved:**
- Visual Studio auto-detection
- ONNX Runtime DLL handling
- Error messages and troubleshooting
- Documentation and examples

---

For additional help, refer to the main README.md or QUICKSTART_WINDOWS.md.
