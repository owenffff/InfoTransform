#!/bin/bash
set -e

echo "================================================"
echo "Starting InfoTransform Services"
echo "================================================"

echo "[1/2] Starting FastAPI backend on port ${PORT:-8000}..."
uv run python app.py &
BACKEND_PID=$!

sleep 5

echo "[2/2] Starting Next.js frontend on port ${FRONTEND_PORT:-3000}..."
cd frontend && npm run start -- -p ${FRONTEND_PORT:-3000} &
FRONTEND_PID=$!

echo "================================================"
echo "Services Started Successfully!"
echo "Backend API: http://localhost:${PORT:-8000}"
echo "Frontend UI: http://localhost:${FRONTEND_PORT:-3000}"
echo "API Docs: http://localhost:${PORT:-8000}/docs"
echo "================================================"

wait -n

exit $?
