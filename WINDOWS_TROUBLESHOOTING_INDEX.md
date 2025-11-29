# 🔍 Windows Build Troubleshooting Index

**Quick Links:** Jump directly to your error

---

## 📋 Common Errors & Solutions

### 1. Visual Studio Not Found

**Error Message:**
```
CMake Error at CMakeLists.txt:2 (project):
  Generator
    Visual Studio 17 2022
  could not find any instance of Visual Studio.
```

**Quick Fix:** [VISUAL_STUDIO_FIX_QUICK_GUIDE.md](VISUAL_STUDIO_FIX_QUICK_GUIDE.md)  
**Full Solution:** [VISUAL_STUDIO_NOT_FOUND_SOLUTION.md](VISUAL_STUDIO_NOT_FOUND_SOLUTION.md)

---

### 2. ONNX Runtime Not Found

**Error Message:**
```
ONNX Runtime not found automatically. You may need to set ONNXRUNTIME_DIR
```

**Quick Fix:** Run the setup script
```powershell
.\setup_onnx_windows.ps1
```

**More Info:** [WINDOWS_BUILD_SOLUTION.md](WINDOWS_BUILD_SOLUTION.md)

---

### 3. CMake Not Found

**Error Message:**
```
'cmake' is not recognized as an internal or external command
```

**Quick Fix:** Install CMake
```powershell
winget install Kitware.CMake
```

Or download from: https://cmake.org/download/

Then restart your terminal and try again.

---

### 4. Python Not Found

**Error Message:**
```
'python' is not recognized as an internal or external command
```

**Quick Fix:**
1. Download Python from: https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart your terminal
4. Run: `python --version` to verify

---

### 5. PowerShell Execution Policy Error

**Error Message:**
```
.\run_demo.ps1 : File cannot be loaded because running scripts is disabled
```

**Quick Fix:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try running the script again.

---

### 6. Missing C++ Build Tools

**Error Message:**
```
LINK : fatal error LNK1104: cannot open file 'MSVCRT.lib'
```

**Cause:** Visual Studio installed without C++ workload

**Quick Fix:**
1. Open "Visual Studio Installer"
2. Click "Modify"
3. Check "Desktop development with C++"
4. Click "Modify" to install

---

### 7. Missing DLL at Runtime

**Error Message:**
```
The code execution cannot proceed because onnxruntime.dll was not found
```

**Quick Fix:** Copy the DLL
```batch
copy onnxruntime-win-x64-1.17.1\lib\onnxruntime.dll cpp\build\Release\
```

**Note:** The automated scripts should do this automatically. If you're building manually, you need to copy it yourself.

---

### 8. PyQt5 Window Not Showing

**Error Message:** Python script runs but no window appears

**Quick Fix:** Reinstall PyQt5
```batch
pip uninstall PyQt5
pip install PyQt5
```

---

### 9. Git Submodules Not Initialized

**Error Message:**
```
fatal: No url found for submodule path '...'
```

**Quick Fix:**
```batch
git submodule update --init --recursive
```

---

### 10. Long Path Issues

**Error Message:**
```
The specified path, file name, or both are too long
```

**Quick Fix:** Enable long paths in Windows
```batch
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f
```

Restart your computer after this change.

---

## 🎯 General Troubleshooting Steps

### Step 1: Use Automated Scripts First

Most issues are avoided by using the automated scripts:

```powershell
# PowerShell (recommended)
.\run_demo.ps1
```

```batch
# Command Prompt
run_demo.bat
```

### Step 2: Clean Build

If something went wrong, start fresh:

```powershell
Remove-Item -Recurse -Force cpp\build
Remove-Item -Recurse -Force models
Remove-Item -Recurse -Force data
.\run_demo.ps1
```

### Step 3: Check Prerequisites

Make sure you have:
- ✅ Python 3.8+
- ✅ Visual Studio 2017+ with C++ workload
- ✅ CMake 3.15+
- ✅ Internet connection (for downloads)

### Step 4: Verify Installation

```powershell
# Check Python
python --version

# Check CMake
cmake --version

# Check Visual Studio
dir "C:\Program Files\Microsoft Visual Studio"

# Check ONNX Runtime
Test-Path onnxruntime-win-x64-1.17.1\lib\onnxruntime.dll
```

---

## 📚 Documentation Reference

### Quick Start Guides
- **[VISUAL_STUDIO_FIX_QUICK_GUIDE.md](VISUAL_STUDIO_FIX_QUICK_GUIDE.md)** - Visual Studio issue quick fix
- **[START_HERE_WINDOWS.md](START_HERE_WINDOWS.md)** - Where to start on Windows
- **[QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)** - Complete Windows setup guide

### Detailed Solutions
- **[VISUAL_STUDIO_NOT_FOUND_SOLUTION.md](VISUAL_STUDIO_NOT_FOUND_SOLUTION.md)** - Complete VS troubleshooting
- **[WINDOWS_BUILD_SOLUTION.md](WINDOWS_BUILD_SOLUTION.md)** - Build process overview
- **[WINDOWS_CONFIG.md](WINDOWS_CONFIG.md)** - Configuration details

### Technical Reference
- **[cpp/README_WINDOWS.md](cpp/README_WINDOWS.md)** - C++ build details
- **[cpp/README_CPP.md](cpp/README_CPP.md)** - C++ API reference
- **[README.md](README.md)** - Main project documentation

---

## 🔄 Decision Tree

```
What's your issue?
│
├─ Visual Studio not found
│  └─ See: VISUAL_STUDIO_FIX_QUICK_GUIDE.md
│
├─ ONNX Runtime not found
│  └─ Run: .\setup_onnx_windows.ps1
│
├─ CMake/Python not found
│  └─ Install the missing tool, then retry
│
├─ Build fails but tools are installed
│  └─ Try clean build (Step 2 above)
│
└─ Everything installed but still failing
   └─ See: QUICKSTART_WINDOWS.md troubleshooting section
```

---

## 🆘 Still Stuck?

1. **Check the full Windows guide:** [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)
2. **Review prerequisites:** Make sure all required tools are installed
3. **Try clean build:** Delete build artifacts and start fresh
4. **Check error messages carefully:** Match them to this index

---

## 💡 Pro Tips

### Use PowerShell (Not CMD)
PowerShell scripts have better error handling and colored output:
```powershell
.\run_demo.ps1
```

### Run from Workspace Root
Always run scripts from the project root directory:
```powershell
cd "D:\Zoppler Projects\DroneSimulation"
.\run_demo.ps1
```

### Check Script Output
The scripts provide detailed feedback. Read the messages carefully - they often contain solutions.

### Developer Command Prompt
For manual CMake commands, use "Developer Command Prompt for VS":
- Start Menu → Search "Developer Command Prompt"
- This automatically sets up the build environment

---

## 📊 Success Checklist

Before building, verify:
- [ ] Python installed and in PATH
- [ ] Visual Studio with C++ workload installed
- [ ] CMake installed and in PATH
- [ ] Internet connection available
- [ ] Running from correct directory

After successful build:
- [ ] No errors in console output
- [ ] `cpp\build\Release\drone_trajectory_cpp.exe` exists
- [ ] `models\drone_trajectory.onnx` exists
- [ ] Can run: `.\cpp\build\Release\drone_trajectory_cpp.exe`

---

**Last Updated:** 2025-11-29  
**Status:** Active and Maintained

---

**Quick Answer:** Most issues are solved by running `.\run_demo.ps1` instead of manual CMake commands! 🚀
