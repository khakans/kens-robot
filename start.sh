#!/bin/bash
# Simple startup script for robot-voice-vision
# Usage: ./start.sh

set -e

# Activate virtualenv
source venv/bin/activate

# Export environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found. Please copy .env.example to .env and fill in values."
    exit 1
fi

# Run main app
python src/main.py
