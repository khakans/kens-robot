# AI Voice & Actuator Robot - Raspberry Pi 4

> Robot berbasis AI LLM OpenAI yang dapat melihat menggunakan kamera, mendeteksi wajah/contour, menggerakkan roda, dan berinteraksi dengan percakapan suara secara realtime.

---

## Fitur

- **Computer Vision**
  - Deteksi wajah menggunakan OpenCV
  - Deteksi kontur/obstacle untuk navigasi
- **Robotik**
  - Kontrol 2 roda: maju, mundur, belok kiri/kanan
  - Interface untuk aktuator motor
- **Voice Interaction**
  - STT (Speech-to-Text) realtime
  - TTS (Text-to-Speech) untuk membalas percakapan
  - Robot dapat berbicara tanpa keyboard
- **AI**
  - Integrasi OpenAI LLM untuk percakapan
  - Memahami instruksi dan membalas secara natural

---

## Hardware

- Raspberry Pi 4 (4GB)
- Kamera Module / USB Webcam
- Speaker + Microphone
- Motor driver untuk 2 roda

---

## Struktur Direktori

kk-robot/
│
├── src/
│ ├── main.py # Entry point program robot
│ │
│ ├── vision/
│ │ ├── camera.py # Class Camera wrapper OpenCV
│ │ ├── detector.py # Face/Contour detection
│ │ └── room_detector.py # Opsional: deteksi ruangan/obstacle
│ │
│ ├── audio/
│ │ ├── stt_vosk.py # Realtime Speech-to-Text
│ │ └── tts.py # Text-to-Speech
│ │
│ ├── control/
│ │ └── drive.py # DifferentialDrive: kontrol motor 2 roda
│ │
│ └── llm/
│ └── llm_client.py # Wrapper OpenAI LLM API
│
├── requirements.txt # Library Python
├── README.md # Dokumentasi project
└── .gitignore


---

## Instalasi

1. **Update Raspberry Pi & Install Dependencies**

Download vosk-model-small-en-us-0.15 model from https://alphacephei.com/vosk/models

sudo apt update && sudo apt upgrade -y
sudo apt install python3-pip python3-opencv ffmpeg libatlas-base-dev -y

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

pip install -r requirements.txt

## Running

1. **with python**
python src/main.py

2. **with script**
chmod +x run.sh
./run.sh