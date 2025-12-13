#!/bin/bash
set -x # Print commands for debugging

echo "Starting TraderCopilot Backend..."
pwd
ls -la

# Ensure we are in the directory of the script
cd "$(dirname "$0")"
echo "Changed to directory: $(pwd)"

# 1. Start the Scheduler in the background
echo "Starting Scheduler..."
# Add current directory to PYTHONPATH to ensure imports work
export PYTHONPATH=$PYTHONPATH:$(pwd)
python scheduler.py &

# 2. Start the API
# Force port 8000 ONLY if not provided by Railway (User Request)
export PORT=${PORT:-8000}
echo "Using PORT: $PORT"
uvicorn main:app --host 0.0.0.0 --port $PORT
