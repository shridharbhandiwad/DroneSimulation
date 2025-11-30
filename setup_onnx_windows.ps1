# ONNX Runtime Setup Script for Windows
# This script downloads and sets up ONNX Runtime for Windows

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ONNX Runtime Setup for Windows" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$ONNX_VERSION = "1.17.1"
$ONNX_PACKAGE = "onnxruntime-win-x64-$ONNX_VERSION"
$ONNX_ZIP = "$ONNX_PACKAGE.zip"
$ONNX_URL = "https://github.com/microsoft/onnxruntime/releases/download/v$ONNX_VERSION/$ONNX_ZIP"
$INSTALL_DIR = "$PSScriptRoot\onnxruntime-win-x64-$ONNX_VERSION"

# Check if already installed
if (Test-Path $INSTALL_DIR) {
    Write-Host "ONNX Runtime is already installed at:" -ForegroundColor Green
    Write-Host "  $INSTALL_DIR" -ForegroundColor White
    Write-Host ""
    Write-Host "To reinstall, delete the directory and run this script again." -ForegroundColor Yellow
    exit 0
}

# Download ONNX Runtime
Write-Host "Downloading ONNX Runtime $ONNX_VERSION for Windows..." -ForegroundColor Cyan
Write-Host "URL: $ONNX_URL" -ForegroundColor Gray
Write-Host ""

try {
    # Create temporary download directory
    $TempDir = "$PSScriptRoot\temp_onnx_download"
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TempDir | Out-Null
    
    $ZipPath = "$TempDir\$ONNX_ZIP"
    
    # Download with progress
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $ONNX_URL -OutFile $ZipPath -UseBasicParsing
    $ProgressPreference = 'Continue'
    
    Write-Host "Download complete" -ForegroundColor Green
    
    # Verify download
    if (-not (Test-Path $ZipPath)) {
        throw "Downloaded file not found"
    }
    
    $FileSize = (Get-Item $ZipPath).Length / 1MB
    Write-Host "File size: $([math]::Round($FileSize, 2)) MB" -ForegroundColor Gray
    Write-Host ""
    
    # Extract
    Write-Host "Extracting ONNX Runtime..." -ForegroundColor Cyan
    Expand-Archive -Path $ZipPath -DestinationPath $PSScriptRoot -Force
    
    Write-Host "Extraction complete" -ForegroundColor Green
    
    # Cleanup
    Remove-Item -Path $TempDir -Recurse -Force
    
    # Verify installation
    Write-Host ""
    Write-Host "Verifying installation..." -ForegroundColor Cyan
    
    $RequiredFiles = @(
        "$INSTALL_DIR\include\onnxruntime_c_api.h",
        "$INSTALL_DIR\include\onnxruntime_cxx_api.h",
        "$INSTALL_DIR\lib\onnxruntime.lib",
        "$INSTALL_DIR\lib\onnxruntime.dll"
    )
    
    $AllFilesFound = $true
    foreach ($file in $RequiredFiles) {
        if (Test-Path $file) {
            Write-Host "  Found: $(Split-Path $file -Leaf)" -ForegroundColor Green
        } else {
            Write-Host "  Missing: $(Split-Path $file -Leaf)" -ForegroundColor Red
            $AllFilesFound = $false
        }
    }
    
    Write-Host ""
    
    if ($AllFilesFound) {
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "ONNX Runtime Setup Complete!" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Installation directory:" -ForegroundColor White
        Write-Host "  $INSTALL_DIR" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "You can now build the C++ components with:" -ForegroundColor Yellow
        Write-Host "  cd cpp" -ForegroundColor White
        Write-Host "  mkdir build" -ForegroundColor White
        Write-Host "  cd build" -ForegroundColor White
        Write-Host "  cmake .. -G ""Visual Studio 17 2022"" -A x64 -DONNXRUNTIME_DIR=$INSTALL_DIR" -ForegroundColor White
        Write-Host "  cmake --build . --config Release" -ForegroundColor White
        Write-Host ""
        Write-Host "Or run the complete demo:" -ForegroundColor Yellow
        Write-Host "  .\run_demo.ps1" -ForegroundColor White
        Write-Host ""
    } else {
        throw "Installation verification failed - some required files are missing"
    }
    
} catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Error during setup" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check your internet connection" -ForegroundColor White
    Write-Host "  2. Verify you can access: $ONNX_URL" -ForegroundColor White
    Write-Host "  3. Try downloading manually and extracting to:" -ForegroundColor White
    Write-Host "     $INSTALL_DIR" -ForegroundColor Cyan
    Write-Host ""
    
    # Cleanup on error
    if (Test-Path $TempDir) {
        Remove-Item -Path $TempDir -Recurse -Force
    }
    
    exit 1
}
