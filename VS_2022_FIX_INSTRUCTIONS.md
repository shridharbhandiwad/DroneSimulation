# 🔧 Fix: Visual Studio 2022 Not Found by CMake

## Your Exact Error
```
CMake Error at CMakeLists.txt:2 (project):
  Generator
    Visual Studio 17 2022
  could not find any instance of Visual Studio.
```

## Quick Diagnosis

Even though you have VS 2022 installed, CMake can't find it. Let's check what's wrong:

### Step 1: Check if C++ Workload is Installed

**This is the #1 reason for this error!**

1. Open **Visual Studio Installer** (search in Start Menu)
2. Find your Visual Studio 2022 installation
3. Click **"Modify"** button
4. Check if **"Desktop development with C++"** is selected

If it's NOT checked:
- ✅ Check the box for "Desktop development with C++"
- Click "Modify" button to install it
- Wait for installation to complete (~5-10 minutes)
- Restart your computer
- Try your CMake command again

### Step 2: Verify VS 2022 Installation

Run this command in PowerShell to check if VS 2022 is properly installed:

```powershell
# Check for VS 2022 Community
Test-Path "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"

# Or VS 2022 Professional
Test-Path "C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvarsall.bat"

# Or VS 2022 Enterprise
Test-Path "C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvarsall.bat"
```

If ALL return `False`, then VS 2022 C++ tools are not installed properly.

### Step 3: Check Which Visual Studio Versions You Have

```powershell
# List all VS installations
dir "C:\Program Files\Microsoft Visual Studio"
```

You'll see folders like:
- `2022` → Use generator: `"Visual Studio 17 2022"`
- `2019` → Use generator: `"Visual Studio 16 2019"`
- `2017` → Use generator: `"Visual Studio 15 2017"`

## ✅ Solutions

### Solution 1: Install C++ Workload (Most Common Fix)

1. **Open Visual Studio Installer**
   - Search "Visual Studio Installer" in Start Menu
   - Click to open

2. **Modify Installation**
   - Find "Visual Studio Community 2022" (or Professional/Enterprise)
   - Click "Modify"

3. **Select C++ Workload**
   - On the "Workloads" tab
   - Check: ✅ **"Desktop development with C++"**
   - This includes:
     - MSVC v143 C++ compiler
     - C++ CMake tools for Windows
     - Windows 10/11 SDK

4. **Install**
   - Click "Modify" button (bottom right)
   - Wait for installation (~5-10 minutes)
   - Restart computer

5. **Try Again**
   ```batch
   cd D:\Zoppler Projects\DroneSimulation\cpp\build
   cmake .. -G "Visual Studio 17 2022" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
   ```

### Solution 2: Use Visual Studio Developer Command Prompt

CMake works best from VS Developer Command Prompt:

1. **Open Developer Command Prompt**
   - Start Menu → Search "Developer Command Prompt for VS 2022"
   - Or: Visual Studio 2022 → Tools → Command Line → Developer Command Prompt

2. **Navigate and Build**
   ```batch
   cd "D:\Zoppler Projects\DroneSimulation\cpp\build"
   cmake .. -G "Visual Studio 17 2022" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
   cmake --build . --config Release
   ```

### Solution 3: Use Your Actual VS Version

If you have VS 2019 instead of 2022:

```batch
# For Visual Studio 2019
cd D:\Zoppler Projects\DroneSimulation\cpp\build
cmake .. -G "Visual Studio 16 2019" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
```

For Visual Studio 2017:
```batch
# For Visual Studio 2017
cmake .. -G "Visual Studio 15 2017" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
```

### Solution 4: List Available Generators

Check what CMake can actually see:

```batch
cmake --help
```

Scroll to the "Generators" section. You'll see what's available on your system.

### Solution 5: Use Automated Script (Easiest!)

The project has scripts that auto-detect your VS version:

```batch
# From the main project directory
cd D:\Zoppler Projects\DroneSimulation

# Use the batch script
run_demo.bat

# Or PowerShell script
powershell -ExecutionPolicy Bypass -File .\run_demo.ps1
```

These scripts will:
- Auto-detect your Visual Studio version
- Download ONNX Runtime if needed
- Build everything correctly

## 🔍 Verification Commands

After installing C++ workload, verify:

```batch
# Check if VS 2022 C++ compiler exists
dir "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC"

# Check if CMake can find it
cmake --help
```

Under "Generators", you should see:
```
Visual Studio 17 2022 [arch] = Generates Visual Studio 2022 project files.
                               Use -A option to specify architecture.
```

## 📋 Complete Clean Build Steps

After fixing the issue:

```batch
# 1. Open Developer Command Prompt for VS 2022

# 2. Navigate to project
cd "D:\Zoppler Projects\DroneSimulation"

# 3. Clean old build
rmdir /s /q cpp\build
mkdir cpp\build
cd cpp\build

# 4. Configure
cmake .. -G "Visual Studio 17 2022" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1

# 5. Build
cmake --build . --config Release

# 6. Run
Release\drone_trajectory_cpp.exe
```

## ❌ Still Not Working?

### Try This Diagnostic:

```batch
# Run this in Command Prompt
where cl.exe
```

If it says "INFO: Could not find files", then C++ compiler is not installed or not in PATH.

### Check VS Installation Log:

1. Go to: `%TEMP%\dd_setup*.log`
2. Open the latest log file
3. Search for "Desktop development with C++"
4. Verify it was installed

### Reinstall Visual Studio:

If all else fails:

1. **Uninstall** Visual Studio 2022 completely
2. **Restart** computer
3. **Download** fresh installer from https://visualstudio.microsoft.com/downloads/
4. **Install** with these workloads selected:
   - ✅ Desktop development with C++
   - ✅ CMake tools for Windows (optional but helpful)
5. **Restart** computer
6. Try build again

## 🎯 Quick Decision Tree

```
Visual Studio Installer → Find VS 2022 → Modify
    │
    └─ Is "Desktop development with C++" checked?
        │
        ├─ NO → Check it → Click Modify → Wait for install → Restart → Build again ✅
        │
        └─ YES → Check VS version in folder:
            │
            ├─ Has 2022 folder → Use: -G "Visual Studio 17 2022"
            ├─ Has 2019 folder → Use: -G "Visual Studio 16 2019"
            └─ Has 2017 folder → Use: -G "Visual Studio 15 2017"
```

## ✅ Expected Success Output

When it works, you'll see:

```
-- Building for: Visual Studio 17 2022
-- Selecting Windows SDK version 10.0.22621.0 to target Windows 10.0.22631.
-- The C compiler identification is MSVC 19.38.33134.0
-- The CXX compiler identification is MSVC 19.38.33134.0
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: C:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC/14.38.33130/bin/Hostx64/x64/cl.exe - skipped
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
...
-- Configuring done
-- Generating done
-- Build files have been written to: D:/Zoppler Projects/DroneSimulation/cpp/build
```

## 📞 Need More Help?

See also:
- [VISUAL_STUDIO_NOT_FOUND_SOLUTION.md](VISUAL_STUDIO_NOT_FOUND_SOLUTION.md) - Detailed VS troubleshooting
- [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md) - Complete Windows setup guide
- [cpp/README_WINDOWS.md](cpp/README_WINDOWS.md) - C++ build documentation

---

**Most likely fix:** Install "Desktop development with C++" workload in Visual Studio Installer!
