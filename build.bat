@echo off
echo ==============================================
echo Building Voice2Prompt Standalone Executable...
echo ==============================================

pyinstaller --noconsole --onefile --clean ^
  --collect-all customtkinter ^
  --name "Voice2Prompt" ^
  main.py

echo ==============================================
echo Build finished! Check dist\Voice2Prompt.exe
echo ==============================================
pause
