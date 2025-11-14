#!/bin/bash

echo "Stopping Issue Tracker Application..."

# Stop frontend
if [ -f /tmp/issue_tracker_frontend.pid ]; then
    FRONTEND_PID=$(cat /tmp/issue_tracker_frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm /tmp/issue_tracker_frontend.pid
fi

# Also kill any node process on port 3000
FRONTEND_PORT_PID=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$FRONTEND_PORT_PID" ]; then
    echo "Stopping frontend process on port 3000..."
    kill $FRONTEND_PORT_PID 2>/dev/null || true
fi

# Stop backend
cd "$(dirname "$0")/backend"
echo "Stopping backend services..."
docker compose down

echo "All services stopped!"
