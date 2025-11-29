# 🔧 Solution: Visual Studio 17 2022 Not Found

## The Error You're Seeing

```
CMake Error at CMakeLists.txt:2 (project):
  Generator
    Visual Studio 17 2022
  could not find any instance of Visual Studio.

-- Configuring incomplete, errors occurred!
```

## What This Means

CMake cannot find Visual Studio 2022 on your system. This happens when:
1. Visual Studio 2022 is not installed, OR
2. You have a different version of Visual Studio, OR
3. Visual Studio is installed but the C++ workload is missing

---

## ✅ Solution Options

### Option 1: Install Visual Studio 2022 (Recommended)

If you don't have Visual Studio 2022:

1. **Download Visual Studio 2022 Community (Free):**
   - Go to: https://visualstudio.microsoft.com/downloads/
   - Click "Download" under "Community 2022"

2. **During Installation, Select:**
   - ✅ "Desktop development with C++"
   - This installs the C++ compiler and tools CMake needs

3. **After Installation:**
   - Restart your computer
   - Try building again

### Option 2: Use Your Existing Visual Studio Version

If you have Visual Studio 2019 or 2017 installed, use the correct generator:

#### For Visual Studio 2019:
```bash
cmake .. -G "Visual Studio 16 2019" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
```

#### For Visual Studio 2017:
```bash
cmake .. -G "Visual Studio 15 2017" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
```

#### Not Sure Which Version You Have?

Check with this command:
```powershell
# PowerShell
dir "C:\Program Files\Microsoft Visual Studio"
```

Or:
```batch
# Command Prompt
dir "C:\Program Files\Microsoft Visual Studio"
```

You'll see folders like:
- `2022` → Use "Visual Studio 17 2022"
- `2019` → Use "Visual Studio 16 2019"
- `2017` → Use "Visual Studio 15 2017"

### Option 3: Use the Automated Scripts (Easiest!)

The project has automated scripts that detect your Visual Studio version automatically:

#### Using PowerShell (Recommended):
```powershell
cd D:\Zoppler Projects\DroneSimulation
.\run_demo.ps1
```

#### Using Command Prompt:
```batch
cd D:\Zoppler Projects\DroneSimulation
run_demo.bat
```

These scripts will:
- ✅ Automatically detect your Visual Studio version
- ✅ Use the correct CMake generator
- ✅ Download ONNX Runtime if needed
- ✅ Build everything correctly

### Option 4: Try MinGW (Alternative Compiler)

If you can't install Visual Studio, you can use MinGW:

1. **Install MinGW-w64:**
   - Download from: https://www.mingw-w64.org/downloads/
   - Or use MSYS2: https://www.msys2.org/

2. **Build with MinGW:**
   ```bash
   cd cpp\build
   cmake .. -G "MinGW Makefiles" -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
   cmake --build .
   ```

---

## 🔍 Verify Your Visual Studio Installation

### Check if C++ Workload is Installed

1. Open "Visual Studio Installer"
2. Find your Visual Studio installation
3. Click "Modify"
4. Ensure "Desktop development with C++" is checked
5. If not, check it and click "Modify" to install

### Verify Installation via Command Line

```powershell
# Check for Visual Studio 2022
Test-Path "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"

# Check for Visual Studio 2019
Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat"

# Check for Visual Studio 2017
Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat"
```

If any return `True`, you have that version installed.

---

## 🎯 Step-by-Step Build Instructions

### After Installing/Verifying Visual Studio:

1. **Close and reopen your terminal**
   - This ensures environment variables are updated

2. **Clean the build directory:**
   ```batch
   cd D:\Zoppler Projects\DroneSimulation\cpp\build
   del /S /Q *
   ```

3. **Run CMake with the correct generator:**
   
   For VS 2022:
   ```batch
   cmake .. -G "Visual Studio 17 2022" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
   ```
   
   For VS 2019:
   ```batch
   cmake .. -G "Visual Studio 16 2019" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
   ```

4. **Build:**
   ```batch
   cmake --build . --config Release
   ```

5. **Run:**
   ```batch
   Release\drone_trajectory_cpp.exe
   ```

---

## 🚨 Common Issues and Fixes

### Issue: "CMake is not recognized"
**Solution:** Install CMake
```powershell
# Using winget (Windows Package Manager)
winget install Kitware.CMake

# Or download from: https://cmake.org/download/
```

### Issue: "ONNX Runtime not found"
**Solution:** The automated script will download it:
```powershell
.\setup_onnx_windows.ps1
```

Or download manually:
1. Go to: https://github.com/microsoft/onnxruntime/releases
2. Download: `onnxruntime-win-x64-1.17.1.zip`
3. Extract to: `D:\Zoppler Projects\DroneSimulation\onnxruntime-win-x64-1.17.1`

### Issue: "Missing onnxruntime.dll"
**Solution:** Copy the DLL:
```batch
copy ..\..\onnxruntime-win-x64-1.17.1\lib\onnxruntime.dll Release\
```

### Issue: Still not working?
**Try the automated scripts:**
```powershell
cd D:\Zoppler Projects\DroneSimulation
.\run_demo.ps1
```

---

## 📋 Quick Decision Tree

```
Do you have Visual Studio installed?
│
├─ No → Install VS 2022 Community (Option 1)
│   └─ Or use MinGW (Option 4)
│
└─ Yes
    │
    ├─ Visual Studio 2022? → Use: -G "Visual Studio 17 2022"
    │
    ├─ Visual Studio 2019? → Use: -G "Visual Studio 16 2019"
    │
    ├─ Visual Studio 2017? → Use: -G "Visual Studio 15 2017"
    │
    └─ Not sure? → Use automated scripts (Option 3)
```

---

## 🎯 Recommended Approach

**For the fastest solution:**

1. **Just run the automated script:**
   ```powershell
   cd D:\Zoppler Projects\DroneSimulation
   .\run_demo.ps1
   ```

2. **It will:**
   - Detect your Visual Studio version automatically
   - Download ONNX Runtime if needed
   - Build everything correctly
   - Run the demo

3. **No manual CMake commands needed!**

---

## 📚 Related Documentation

- [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md) - Complete Windows setup guide
- [WINDOWS_BUILD_SOLUTION.md](WINDOWS_BUILD_SOLUTION.md) - Windows build overview
- [WINDOWS_CONFIG.md](WINDOWS_CONFIG.md) - Detailed configuration guide

---

## 💡 Pro Tips

1. **Use Developer Command Prompt for VS**
   - Start Menu → Search "Developer Command Prompt"
   - This automatically sets up the build environment

2. **Check CMake version**
   ```bash
   cmake --version
   ```
   Should be 3.15 or higher

3. **List available CMake generators**
   ```bash
   cmake --help
   ```
   Look under "Generators" section

---

## ✅ Expected Output When It Works

When CMake runs successfully, you should see:

```
-- The C compiler identification is MSVC 19.xx.xxxxx.x
-- The CXX compiler identification is MSVC 19.xx.xxxxx.x
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Check for working C compiler: C:/Program Files/Microsoft Visual Studio/.../cl.exe - skipped
-- Detecting C compile features
-- Detecting C compile features - done
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
...
ONNX Runtime include: D:/Zoppler Projects/DroneSimulation/onnxruntime-win-x64-1.17.1/include
ONNX Runtime library: D:/Zoppler Projects/DroneSimulation/onnxruntime-win-x64-1.17.1/lib/onnxruntime.lib
Found ONNX Runtime DLL: D:/Zoppler Projects/DroneSimulation/onnxruntime-win-x64-1.17.1/lib/onnxruntime.dll
...
-- Configuring done
-- Generating done
-- Build files have been written to: D:/Zoppler Projects/DroneSimulation/cpp/build
```

---

**Status:** Ready to use  
**Date:** 2025-11-29  
**Next Step:** Choose one of the solution options above and try again!
