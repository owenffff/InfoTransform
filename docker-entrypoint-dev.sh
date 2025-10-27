#!/bin/bash
set -e

# Trap SIGTERM and SIGINT for graceful shutdown
cleanup() {
    echo ""
    echo "================================================"
    echo "Shutting down services gracefully..."
    echo "================================================"

    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill -TERM "$BACKEND_PID" 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill -TERM "$FRONTEND_PID" 2>/dev/null || true
    fi

    # Wait for processes to terminate
    wait 2>/dev/null || true

    echo "Cleanup completed"
    exit 0
}

trap cleanup SIGTERM SIGINT

echo "================================================"
echo "Starting InfoTransform Development Environment"
echo "================================================"
echo "Environment: ${ENV:-development}"
echo "Backend Port: ${BACKEND_PORT:-8000}"
echo "Frontend Port: ${PORT:-3000}"
echo "Quiet Mode: ${QUIET_MODE:-false}"
echo "================================================"

# Ensure required directories exist
mkdir -p data/uploads data/temp_extracts logs
mkdir -p data/uploads/review_sessions data/uploads/review_documents
mkdir -p backend/infotransform/data

# Start backend with improved error handling
echo "[1/2] Starting FastAPI backend in development mode..."
if ! uv run python app.py > /tmp/backend.log 2>&1 &
then
    echo "ERROR: Failed to start backend server"
    cat /tmp/backend.log
    exit 1
fi
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 5

# Check if backend is still running
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "ERROR: Backend process died unexpectedly"
    cat /tmp/backend.log
    exit 1
fi

# Start frontend
echo "[2/2] Starting Next.js frontend in development mode..."
cd frontend
if ! npm run dev -- -p ${PORT:-3000} > /tmp/frontend.log 2>&1 &
then
    echo "ERROR: Failed to start frontend server"
    cat /tmp/frontend.log
    exit 1
fi
FRONTEND_PID=$!
cd ..
echo "Frontend started (PID: $FRONTEND_PID)"

echo "================================================"
echo "Development Services Started Successfully!"
echo "================================================"
echo "Backend API:    http://localhost:${BACKEND_PORT:-8000}"
echo "Frontend UI:    http://localhost:${PORT:-3000}"
echo "API Docs:       http://localhost:${BACKEND_PORT:-8000}/docs"
echo "Health Check:   http://localhost:${BACKEND_PORT:-8000}/health"
echo "================================================"
echo "Hot-reloading enabled for both services"
echo "Press Ctrl+C to stop all services"
echo "================================================"

# Wait for either process to exit
wait -n

# If we get here, one of the processes has exited
EXIT_CODE=$?
echo "A service has stopped unexpectedly (exit code: $EXIT_CODE)"
cleanup
