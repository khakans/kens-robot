# src/vision/detector.py
import cv2
from typing import List, Tuple


class FaceDetector:
    def __init__(self, cascade_path: str = "haarcascade_frontalface_default.xml"):
        full_path = cv2.data.haarcascades + cascade_path
        self.detector = cv2.CascadeClassifier(full_path)

        if self.detector.empty():
            raise RuntimeError(f"❌ Failed to load Haar cascade: {full_path}")

    def detect(self, frame) -> List[Tuple[int, int, int, int]]:
        if frame is None:
            return []

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            print(f"[Error] cvtColor failed: {e}")
            return []

        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
        )

        # pastikan return selalu list of tuple
        return [tuple(f) for f in faces]
