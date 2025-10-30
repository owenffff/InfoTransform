@echo off
REM Windows setup script for InfoTransform
REM Run this once after cloning the repository

echo ========================================
echo InfoTransform - Windows Setup Script
echo ========================================
echo.

REM Check if Git is installed (optional)
git --version >nul 2>&1
if errorlevel 1 (
    echo Warning: Git is not installed or not in PATH
    echo Git is recommended but not required for running InfoTransform
    echo You can install it later from: https://git-scm.com/download/win
    echo.
    echo Continuing with setup...
    echo.
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 18 or higher from: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.11 or higher from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo Error: uv is not installed or not in PATH
    echo Please install uv from: https://github.com/astral-sh/uv
    echo.
    echo Quick install: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    pause
    exit /b 1
)

echo All prerequisites are installed!
echo.

REM Install root Node.js dependencies
echo [1/5] Installing root Node.js dependencies...
call npm install
if errorlevel 1 (
    echo Failed to install root Node.js dependencies
    pause
    exit /b 1
)
echo Root Node.js dependencies installed successfully
echo.

REM Install frontend Node.js dependencies
echo [2/5] Installing frontend Node.js dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo Failed to install frontend Node.js dependencies
    cd ..
    pause
    exit /b 1
)
cd ..

REM Verify frontend dependencies
if not exist frontend\node_modules (
    echo ERROR: Frontend dependencies failed to install!
    echo Please check the error messages above and try again.
    pause
    exit /b 1
)
echo Frontend Node.js dependencies installed successfully
echo.

REM Create Python virtual environment
echo [3/5] Creating Python virtual environment...
call uv venv
if errorlevel 1 (
    echo Failed to create virtual environment
    pause
    exit /b 1
)
echo Virtual environment created successfully
echo.

REM Install Python dependencies
echo [4/5] Installing Python dependencies...
call uv sync
if errorlevel 1 (
    echo Failed to install Python dependencies
    pause
    exit /b 1
)
echo Python dependencies installed successfully
echo.

REM Setup .env file
echo [5/5] Setting up environment configuration...
if not exist .env (
    echo Copying .env.example to .env...
    copy .env.example .env >nul
    echo.
    echo IMPORTANT: Please edit .env file and add your OPENAI_API_KEY
    echo You can find the file at: %CD%\.env
) else (
    echo .env file already exists, skipping...
)
echo.

REM Validate port configuration in .env
echo Validating port configuration...
findstr /C:"NEXT_PUBLIC_BACKEND_PORT" .env >nul 2>&1
if errorlevel 1 (
    echo WARNING: NEXT_PUBLIC_BACKEND_PORT not found in .env
    echo This may cause connection issues between frontend and backend.
    echo Please check your .env file against .env.example
)

findstr /C:"BACKEND_PORT" .env >nul 2>&1
if errorlevel 1 (
    echo WARNING: BACKEND_PORT not found in .env
    echo Backend may use incorrect port.
)

REM Display current port configuration
echo.
echo Current port configuration:
findstr /C:"PORT=" .env 2>nul
echo.
echo CRITICAL: Ensure BACKEND_PORT and NEXT_PUBLIC_BACKEND_PORT have THE SAME VALUE!
echo.

REM Create data directories
if not exist data\uploads mkdir data\uploads
if not exist data\temp_extracts mkdir data\temp_extracts

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and verify your OPENAI_API_KEY
echo 2. IMPORTANT: Ensure BACKEND_PORT and NEXT_PUBLIC_BACKEND_PORT match!
echo    Current values shown above - they should be identical.
echo 3. Run 'dev.bat' to start the development server
echo    OR run 'npm run dev' from the command line
echo.
echo The application will be available at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000 (or your configured BACKEND_PORT)
echo - API Docs: http://localhost:8000/docs
echo.
echo ========================================
echo TROUBLESHOOTING
echo ========================================
echo If you experience issues:
echo.
echo 1. Frontend hangs with no backend logs:
echo    - Check that BACKEND_PORT = NEXT_PUBLIC_BACKEND_PORT in .env
echo    - Restart both frontend and backend after editing .env
echo    - Press F12 in browser, check Console for [API-URL] logs
echo.
echo 2. First run takes 30-60 seconds:
echo    - This is normal! Next.js builds on first startup
echo    - Wait for "Ready in XXXms" message
echo.
echo 3. "Module not found" errors:
echo    - Run: npm install (in root directory)
echo    - Run: cd frontend && npm install
echo.
echo 4. Python errors:
echo    - Run: uv sync
echo    - Ensure Python 3.11+ is installed
echo.
echo For detailed help, see: WINDOWS_TROUBLESHOOTING.md
echo ========================================
echo.
pause
