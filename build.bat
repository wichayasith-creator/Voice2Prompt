@echo off
echo ==============================================
echo Building Voice2Prompt Standalone Executable...
echo ==============================================

pyinstaller --noconsole --onefile --clean ^
  --collect-all customtkinter ^
  --name "Voice2Prompt" ^
  main.py

echo ==============================================
if exist "dist\Voice2Prompt.exe" (
    echo Build finished! Check dist\Voice2Prompt.exe
    echo.
    echo Generating SHA256 Checksum for Release Verification:
    certutil -hashfile "dist\Voice2Prompt.exe" SHA256
) else (
    echo Build failed: dist\Voice2Prompt.exe was not created.
)
echo ==============================================
pause
