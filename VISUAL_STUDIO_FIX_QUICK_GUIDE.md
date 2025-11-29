# ⚡ Quick Fix: Visual Studio Not Found Error

## The Error

```
CMake Error at CMakeLists.txt:2 (project):
  Generator
    Visual Studio 17 2022
  could not find any instance of Visual Studio.
```

---

## ⚡ Fast Solutions (Pick One)

### 🎯 Solution 1: Use Automated Script (Easiest - 30 seconds)

Just run the automated script - it will detect your Visual Studio version automatically:

**PowerShell:**
```powershell
cd "D:\Zoppler Projects\DroneSimulation"
.\run_demo.ps1
```

**Command Prompt:**
```batch
cd "D:\Zoppler Projects\DroneSimulation"
run_demo.bat
```

The script automatically:
- ✅ Detects your Visual Studio version
- ✅ Uses the correct CMake generator
- ✅ Builds everything correctly

---

### 🔧 Solution 2: Install Visual Studio 2022 (10 minutes)

If you don't have Visual Studio:

1. **Download:** https://visualstudio.microsoft.com/downloads/
2. **Install:** Select "Desktop development with C++" workload
3. **Restart** your computer
4. **Run** the automated script (Solution 1)

---

### 🔄 Solution 3: Use Your Existing Visual Studio

If you have VS 2019 or 2017, use the correct generator:

**Visual Studio 2019:**
```batch
cd cpp\build
cmake .. -G "Visual Studio 16 2019" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
cmake --build . --config Release
```

**Visual Studio 2017:**
```batch
cd cpp\build
cmake .. -G "Visual Studio 15 2017" -A x64 -DONNXRUNTIME_DIR=..\..\onnxruntime-win-x64-1.17.1
cmake --build . --config Release
```

**Not sure which version?** Check:
```powershell
dir "C:\Program Files\Microsoft Visual Studio"
```

---

## 📋 Check If You Have Visual Studio

Run this in PowerShell:

```powershell
# Check for VS 2022
Test-Path "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"

# Check for VS 2019
Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvarsall.bat"

# Check for VS 2017
Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\2017\Community\VC\Auxiliary\Build\vcvarsall.bat"
```

If any returns `True`, you have that version. Use the matching generator in Solution 3.

---

## 🚨 Common Mistakes

### ❌ Wrong: Directory exists but C++ tools not installed
Visual Studio might be installed without the C++ workload.

**Fix:**
1. Open "Visual Studio Installer"
2. Click "Modify" on your installation
3. Check "Desktop development with C++"
4. Click "Modify" to install

### ❌ Wrong: Using wrong Visual Studio version in command
You have VS 2019 but used "Visual Studio 17 2022" generator.

**Fix:** Use the correct generator for your version (see Solution 3)

### ❌ Wrong: Running in wrong directory
You're in the workspace root but CMake commands need to be in `cpp/build`.

**Fix:** Use the automated script (Solution 1) - it handles directories automatically

---

## 🎯 Recommended Path

1. **Try Solution 1** (automated script) - works 90% of the time
2. **If no Visual Studio detected:**
   - Check if you have it installed (see "Check If You Have Visual Studio" above)
   - If yes: Make sure C++ workload is installed
   - If no: Install VS 2022 (Solution 2)
3. **Still having issues?** See full guide: `VISUAL_STUDIO_NOT_FOUND_SOLUTION.md`

---

## 🔗 Additional Resources

- **Full solution guide:** [VISUAL_STUDIO_NOT_FOUND_SOLUTION.md](VISUAL_STUDIO_NOT_FOUND_SOLUTION.md)
- **Windows setup guide:** [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)
- **Windows build overview:** [WINDOWS_BUILD_SOLUTION.md](WINDOWS_BUILD_SOLUTION.md)

---

## ✅ What Success Looks Like

After fixing, you should see:

```
Detected Visual Studio 2022 (Community edition)
Configuring with CMake...
ONNX Runtime directory: D:\Zoppler Projects\DroneSimulation\onnxruntime-win-x64-1.17.1
...
-- Configuring done
-- Generating done
-- Build files have been written to: D:/Zoppler Projects/DroneSimulation/cpp/build
Building...
✓ C++ code built successfully
```

---

**Bottom Line:** Just run `.\run_demo.ps1` - it handles everything automatically! 🚀
