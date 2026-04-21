@echo off
echo ==========================================
echo Building Window Helper Executable...
echo ==========================================

:: Ensure the target directory exists so PyInstaller doesn't complain
if not exist ".\src\assets\bin" mkdir ".\src\assets\bin"

:: Run the optimized PyInstaller command via uv
uv run pyinstaller --onefile --noconsole --clean --distpath=".\src\assets\bin" --workpath=".\build" --icon=".\src\assets\images\icon.ico" .\helpers\window_helper.py

echo.
if %errorlevel% equ 0 (
    echo ==========================================
    echo Build Successful! 
    echo Executable is located at: .\src\assets\bin\window_helper.exe
    echo ==========================================
) else (
    echo ==========================================
    echo Build Failed. Check the error log above.
    echo ==========================================
)
pause