#!/bin/bash
# Script to install dependencies for robot-voice-vision

set -e

echo "Updating system..."
sudo apt update && sudo apt upgrade -y

echo "Installing system packages..."
sudo apt install -y python3-venv python3-pip build-essential \
    libatlas-base-dev libblas-dev liblapack-dev \
    libjpeg-dev portaudio19-dev libasound2-dev \
    git curl

echo "Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Done. You can now copy .env.example to .env and run ./start.sh"
