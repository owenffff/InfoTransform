#!/bin/bash
set -e

echo "================================================"
echo "Starting InfoTransform Development Environment"
echo "================================================"

echo "[1/2] Starting FastAPI backend in development mode on port ${PORT:-8000}..."
uv run python app.py &
BACKEND_PID=$!

sleep 5

echo "[2/2] Starting Next.js frontend in development mode on port ${FRONTEND_PORT:-3000}..."
cd frontend && npm run dev -- -p ${FRONTEND_PORT:-3000} &
FRONTEND_PID=$!

echo "================================================"
echo "Development Services Started Successfully!"
echo "Backend API: http://localhost:${PORT:-8000}"
echo "Frontend UI: http://localhost:${FRONTEND_PORT:-3000}"
echo "API Docs: http://localhost:${PORT:-8000}/docs"
echo "================================================"
echo "Hot-reloading enabled for both services"
echo "================================================"

wait -n

exit $?
