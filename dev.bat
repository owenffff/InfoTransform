@echo off
REM Windows batch script to run InfoTransform development server
REM This is a convenience wrapper around npm run dev

echo Starting InfoTransform development server...
echo.

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found!
    echo Please copy .env.example to .env and configure your API keys.
    echo.
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist node_modules (
    echo Installing Node.js dependencies...
    call npm install
    if errorlevel 1 (
        echo Failed to install Node.js dependencies
        pause
        exit /b 1
    )
)

REM Check if Python virtual environment exists
if not exist .venv (
    echo Creating Python virtual environment...
    call uv venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        echo Please ensure 'uv' is installed: https://github.com/astral-sh/uv
        pause
        exit /b 1
    )
    
    echo Installing Python dependencies...
    call uv sync
    if errorlevel 1 (
        echo Failed to install Python dependencies
        pause
        exit /b 1
    )
)

REM Start the development server
echo.
echo Starting both backend and frontend servers...
echo Frontend will be available at: http://localhost:3000
echo Backend API will be available at: http://localhost:8000
echo API docs: http://localhost:8000/docs
echo.

call npm run dev
