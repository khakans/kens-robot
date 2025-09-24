"""
Application configuration loader.
Reads environment variables and exposes them as constants.
"""

import os
from dotenv import load_dotenv

# load .env if exists
load_dotenv()

# API Keys
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# Audio
STT_ENGINE: str = os.getenv("STT_ENGINE", "vosk")
TTS_ENGINE: str = os.getenv("TTS_ENGINE", "pyttsx3")

# Camera
CAMERA_DEVICE_INDEX: int = int(os.getenv("CAMERA_DEVICE_INDEX", 0))
CAMERA_WIDTH: int = int(os.getenv("CAMERA_WIDTH", 640))
CAMERA_HEIGHT: int = int(os.getenv("CAMERA_HEIGHT", 480))

# Motors
LEFT_MOTOR_FORWARD_PIN: int = int(os.getenv("LEFT_MOTOR_FORWARD_PIN", 17))
LEFT_MOTOR_BACKWARD_PIN: int = int(os.getenv("LEFT_MOTOR_BACKWARD_PIN", 18))
RIGHT_MOTOR_FORWARD_PIN: int = int(os.getenv("RIGHT_MOTOR_FORWARD_PIN", 22))
RIGHT_MOTOR_BACKWARD_PIN: int = int(os.getenv("RIGHT_MOTOR_BACKWARD_PIN", 23))

# Vosk
VOSK_MODEL_PATH: str = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-en-us-0.15")
