@echo off
REM ONNX Runtime Setup Script for Windows (Batch version)
REM This script calls the PowerShell version

echo ==========================================
echo ONNX Runtime Setup for Windows
echo ==========================================
echo.

REM Check if PowerShell is available
where powershell >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: PowerShell is not available
    echo Please run setup_onnx_windows.ps1 directly in PowerShell
    exit /b 1
)

REM Run PowerShell script
powershell -ExecutionPolicy Bypass -File "%~dp0setup_onnx_windows.ps1"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Setup completed successfully!
) else (
    echo.
    echo Setup failed. Please check the error messages above.
    exit /b 1
)
