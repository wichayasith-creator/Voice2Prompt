@echo off
if not exist "dist\Voice2Prompt.exe" (
    echo [ERROR] dist\Voice2Prompt.exe not found. Please run build.bat first.
    exit /b 1
)
echo ==============================================
echo SHA256 Checksum for dist\Voice2Prompt.exe:
echo ==============================================
certutil -hashfile "dist\Voice2Prompt.exe" SHA256
certutil -hashfile "dist\Voice2Prompt.exe" SHA256 > "dist\Voice2Prompt.exe.sha256.txt"
echo.
echo Saved to dist\Voice2Prompt.exe.sha256.txt
