#!/bin/bash
set -e

# Trap SIGTERM and SIGINT for graceful shutdown
cleanup() {
    echo ""
    echo "================================================"
    echo "Shutting down services gracefully..."
    echo "================================================"

    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend workers (PID: $BACKEND_PID)..."
        kill -TERM "$BACKEND_PID" 2>/dev/null || true
        # Wait for graceful shutdown (max 30 seconds)
        for i in {1..30}; do
            if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
                echo "Backend stopped gracefully"
                break
            fi
            sleep 1
        done
        # Force kill if still running
        kill -9 "$BACKEND_PID" 2>/dev/null || true
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill -TERM "$FRONTEND_PID" 2>/dev/null || true
        # Wait for graceful shutdown (max 10 seconds)
        for i in {1..10}; do
            if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
                echo "Frontend stopped gracefully"
                break
            fi
            sleep 1
        done
        # Force kill if still running
        kill -9 "$FRONTEND_PID" 2>/dev/null || true
    fi

    echo "Cleanup completed"
    exit 0
}

trap cleanup SIGTERM SIGINT

echo "================================================"
echo "Starting InfoTransform Production Environment"
echo "================================================"
echo "Environment: ${ENV:-production}"
echo "Workers: ${WORKERS:-4}"
echo "Log Level: ${LOG_LEVEL:-info}"
echo "Backend Port: ${BACKEND_PORT:-8000}"
echo "Frontend Port: ${PORT:-3000}"
echo "================================================"

# Ensure required directories exist with proper permissions
mkdir -p data/uploads data/temp_extracts logs
mkdir -p data/uploads/review_sessions data/uploads/review_documents
mkdir -p backend/infotransform/data

# Validate environment
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY environment variable is required"
    exit 1
fi

# Start backend with uvicorn workers
echo "[1/2] Starting FastAPI backend with ${WORKERS:-4} workers..."
WORKERS=${WORKERS:-4}
LOG_LEVEL=${LOG_LEVEL:-info}
MAX_REQUESTS=${MAX_REQUESTS:-1000}
MAX_REQUESTS_JITTER=${MAX_REQUESTS_JITTER:-50}

uv run uvicorn infotransform.main:app \
    --host 0.0.0.0 \
    --port ${BACKEND_PORT:-8000} \
    --workers ${WORKERS} \
    --log-level ${LOG_LEVEL} \
    --access-log \
    --limit-concurrency 100 \
    --timeout-keep-alive 5 \
    --max-requests ${MAX_REQUESTS} \
    --max-requests-jitter ${MAX_REQUESTS_JITTER} \
    2>&1 | tee -a logs/backend.log &

BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to be healthy
echo "Waiting for backend to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f http://localhost:${BACKEND_PORT:-8000}/health > /dev/null 2>&1; then
        echo "Backend is healthy and ready!"
        break
    fi

    # Check if backend process is still running
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "ERROR: Backend process died during startup"
        tail -50 logs/backend.log
        exit 1
    fi

    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "ERROR: Backend failed to become healthy within timeout"
    tail -50 logs/backend.log
    cleanup
    exit 1
fi

# Start frontend with Next.js production server
echo "[2/2] Starting Next.js frontend in production mode..."
cd frontend

PORT=${PORT:-3000} npm run start 2>&1 | tee -a ../logs/frontend.log &

FRONTEND_PID=$!
cd ..
echo "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
sleep 5

# Verify frontend is running
if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    echo "ERROR: Frontend process died during startup"
    tail -50 logs/frontend.log
    cleanup
    exit 1
fi

echo "================================================"
echo "Production Services Started Successfully!"
echo "================================================"
echo "Backend API:    http://localhost:${BACKEND_PORT:-8000}"
echo "Frontend UI:    http://localhost:${PORT:-3000}"
echo "API Docs:       http://localhost:${BACKEND_PORT:-8000}/docs"
echo "Health Check:   http://localhost:${BACKEND_PORT:-8000}/health"
echo "================================================"
echo "Workers:        ${WORKERS}"
echo "Log Level:      ${LOG_LEVEL}"
echo "Max Requests:   ${MAX_REQUESTS}"
echo "================================================"
echo "Logs are being written to:"
echo "  Backend:  logs/backend.log"
echo "  Frontend: logs/frontend.log"
echo "================================================"

# Monitor processes
while true; do
    # Check backend
    if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
        echo "ERROR: Backend process has stopped"
        tail -50 logs/backend.log
        cleanup
        exit 1
    fi

    # Check frontend
    if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
        echo "ERROR: Frontend process has stopped"
        tail -50 logs/frontend.log
        cleanup
        exit 1
    fi

    # Sleep before next check
    sleep 30
done
