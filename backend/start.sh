#!/bin/bash
echo "Starting TraderCopilot Backend..."

# 1. Start the Scheduler in the background
echo "Starting Scheduler..."
python scheduler.py &

# 2. Start the API
# Force port 8080 to match Railway UI configuration
export PORT=8080
echo "Using PORT: $PORT"
uvicorn main:app --host 0.0.0.0 --port $PORT
