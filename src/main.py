import threading
import platform
import time
import os
import traceback
import logging
from queue import Queue, Empty

from vision.camera import Camera
from vision.detector import FaceDetector
from vision.room_detector import RoomDetector
from audio.stt_vosk import VoskSTT
from audio.tts import TTS
from llm.llm_client import LLMClient

logging.basicConfig(level=logging.INFO)

# coba import DifferentialDrive
try:
    from control.drive import DifferentialDrive
    DRIVE_AVAILABLE = True
except (ImportError, RuntimeError):
    DRIVE_AVAILABLE = False

# fallback MockDrive
class MockDrive:
    def forward(self, speed=0.6):
        print(f"[MOCK] Forward at {speed}")
    def backward(self, speed=0.6):
        print(f"[MOCK] Backward at {speed}")
    def stop(self):
        print("[MOCK] Stop")
    def turn_left(self, speed=0.5, duration=None):
        print("[MOCK] Turn left")
    def turn_right(self, speed=0.5, duration=None):
        print("[MOCK] Turn right")

# Config
DEBUG_VISION = os.getenv("DEBUG_VISION", "0") == "1"
USE_MOCK = os.getenv("MOCK_DRIVE", "1") == "1"

# =====================
# Helper: deskripsi scene dan message
# =====================
def prepare_user_message(user_text, scene_state):
    text = user_text.strip()

    # Kata kunci untuk menanyakan scene
    scene_keywords = [
        "lihat", "around", "apa",
        "happening", "scene",
        "lingkungan", "environment"
        "see", "saw", "describe"
    ]

    if any(word in text.lower() for word in scene_keywords):
        faces = scene_state.get("faces", [])
        objects = scene_state.get("objects", [])
        scene_desc = describe_scene_natural(faces, objects)
        text += f". Scene: {scene_desc}"

    return {"role": "user", "content": text}

def describe_scene_natural(faces, objects):
    desc = []
    if faces:
        if len(faces) == 1:
            desc.append("i see one person in front of me")
        else:
            desc.append("i see {} people in front of me".format(len(faces)))
    if objects:
        obj_list = [o.get("label", "benda") for o in objects]
        desc.append(f"i see {', '.join(obj_list)} in front of me")
    if not desc:
        return "i see nothing in front of me"
    return "; ".join(desc)

# =====================
# Vision worker
# =====================
def vision_worker(cam, face_detector, room_detector, drive, stop_event, scene_state):
    while not stop_event.is_set():
        try:
            ret, frame = next(cam.frames(), (False, None))
            if not ret or frame is None:
                time.sleep(0.05)
                continue

            faces = face_detector.detect(frame)
            frame, objects = room_detector.detect(frame)

            if faces:
                print("🙂 Face detected:", faces)
                drive.stop()

            if objects:
                for o in objects:
                    print(f"📦 {o['label']} (accuracy: {o.get('confidence',0):.2f}) at {o.get('bbox')}")

            scene_state["faces"] = faces
            scene_state["objects"] = objects

        except Exception as e:
            print("[ERROR][vision_worker]:", e)
            traceback.print_exc()
            time.sleep(1)

# =====================
# Voice worker
# =====================
def voice_worker(stt, tts_queue, llm, drive, stop_event, scene_state):
    commands = {
        ("maju","forward"): lambda lang: (drive.forward(0.6), tts_queue.put(("Siap, maju" if lang=="en" else "Okay, moving forward", lang))),
        ("stop","berhenti"): lambda lang: (drive.stop(), tts_queue.put(("Berhenti" if lang=="en" else "Stopped", lang)))
    }

    last_scene_send = 0
    while not stop_event.is_set():
        try:
            result = stt.listen_once(timeout=3)  # timeout lebih panjang
            if not result:
                continue

            # Tangani STT yang return string saja atau tuple
            if isinstance(result, tuple):
                text, lang = result
            else:
                text = result
                lang = "en"  # default bahasa

            if not text:
                continue

            print(f"Heard ({lang}): {text}")
            
            # Cek perintah robot
            executed = False
            for keys, action in commands.items():
                if any(k.lower() in text.lower() for k in keys):
                    action(lang)
                    executed = True
                    break

            if not executed:
                # Hanya tambahkan scene jika user menanyakan
                user_msg = prepare_user_message(text, scene_state)
                resp = llm.chat([user_msg])
                if resp:
                    tts_queue.put((resp, lang))

        except Exception as e:
            print("[ERROR][voice_worker]:", e)
            import traceback
            traceback.print_exc()
            import time
            time.sleep(0.1)

# =====================
# TTS worker
# =====================
def tts_worker(tts, tts_queue, stop_event):
    while not stop_event.is_set():
        try:
            text, lang = tts_queue.get(timeout=0.1)
        except Empty:
            continue
        try:
            if text:
                tts.say(text, lang)
        except Exception as e:
            print("[ERROR][tts_worker]:", e)

# =====================
# Main
# =====================
if __name__ == "__main__":
    stop_event = threading.Event()
    tts_queue = Queue()
    scene_state = {"faces": [], "objects": []}

    try:
        cam = Camera()
        detector = FaceDetector()
        room_detector = RoomDetector()

        if DRIVE_AVAILABLE and not USE_MOCK and platform.system() != "Darwin":
            drive = DifferentialDrive(left_pins=(17,18), right_pins=(22,23))
            print("Using Raspberry Pi DifferentialDrive")
        else:
            drive = MockDrive()
            print("Using MockDrive")

        stt = VoskSTT(model_path="models/vosk-model-small-en-us-0.15")
        tts = TTS()
        llm = LLMClient(system_prompt="You are a witty and friendly robot that loves to joke.")

        vision_thread = threading.Thread(
            target=vision_worker,
            args=(cam, detector, room_detector, drive, stop_event, scene_state),
            daemon=True
        )
        voice_thread = threading.Thread(
            target=voice_worker,
            args=(stt, tts_queue, llm, drive, stop_event, scene_state),
            daemon=True
        )
        tts_thread = threading.Thread(
            target=tts_worker,
            args=(tts, tts_queue, stop_event),
            daemon=True
        )

        vision_thread.start()
        voice_thread.start()
        tts_thread.start()

        vision_thread.join()
        voice_thread.join()
        tts_thread.join()

    except KeyboardInterrupt:
        print("Shutting down robot...")
        stop_event.set()
    except Exception as e:
        print("[FATAL ERROR]:", e)
        traceback.print_exc()
        stop_event.set()