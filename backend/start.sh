#!/bin/bash
echo "Starting TraderCopilot Backend..."
# Force port 8080 to match Railway UI configuration
export PORT=8080
echo "Using PORT: $PORT"
uvicorn main:app --host 0.0.0.0 --port $PORT
