#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the script directory
cd "$SCRIPT_DIR" || exit 1

# Check if the virtual environment exists
if [ -d "venv" ]; then
    # Activate the virtual environment
    source venv/bin/activate
else
    echo "Warning: No virtual environment found at $SCRIPT_DIR/venv"
    echo "Attempting to run without virtual environment..."
fi

# Run the application
# Use python3 to ensure we're using Python 3
python3 main.py
