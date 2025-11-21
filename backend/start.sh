#!/bin/bash
echo "Starting TraderCopilot Backend..."
export PORT="${PORT:-8080}"
echo "Using PORT: $PORT"
uvicorn main:app --host 0.0.0.0 --port $PORT
