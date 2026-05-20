@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo    FINGER GUN DUCK HUNTER - LAUNCHER
echo ==========================================
echo.

:: 1. Try to find Python in the virtual environment first
if exist ".venv\Scripts\python.exe" (
    echo [OK] Virtual environment detected.
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    :: 2. Fallback to system python
    python --version >nul 2>&1
    if !errorlevel! equ 0 (
        echo [!] Virtual environment not found, using system Python...
        set "PYTHON_EXE=python"
    ) else (
        echo [ERROR] Python not found in system PATH or .venv folder.
        echo.
        echo Please ensure Python is installed and either:
        echo 1. Added to your Windows PATH
        echo 2. Or a virtual environment is created in a '.venv' folder
        echo.
        pause
        exit /b 1
    )
)

:: 3. Check for main.py
if not exist "main.py" (
    echo [ERROR] main.py not found in the current directory.
    pause
    exit /b 1
)

:: 4. Run the game
echo [OK] Starting game...
echo.
"%PYTHON_EXE%" main.py

if !errorlevel! neq 0 (
    echo.
    echo [!] Game closed with an error (Code: !errorlevel!)
    pause
)

endlocal
