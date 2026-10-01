#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
RUNNING_PID=$(pgrep -f "$SCRIPT_DIR/main.py")

if [ -n "$RUNNING_PID" ]; then
    echo "🛑 Deteniendo Call Recorder (PID: $RUNNING_PID)..."
    kill $RUNNING_PID
    echo "✅ Call Recorder detenido."
else
    echo "ℹ️  Call Recorder no está en ejecución."
fi
