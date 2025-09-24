from typing import Iterator, Tuple, Optional
import cv2
import logging
import platform

logger = logging.getLogger(__name__)


class Camera:
    def __init__(self, device_index: Optional[int] = None, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.cap = None

        # cek OS
        self.is_windows = platform.system() == "Windows"

        # coba device index manual dulu
        if device_index is not None:
            self.cap = self._open_camera(device_index)

        # jika gagal atau device_index None, coba scan 0-5
        if self.cap is None or not self.cap.isOpened():
            logger.info("🔍 Scanning available cameras...")
            for i in range(6):
                self.cap = self._open_camera(i)
                if self.cap is not None and self.cap.isOpened():
                    logger.info("✅ Camera found at index %s", i)
                    break

        if self.cap is None or not self.cap.isOpened():
            logger.warning("⚠️ No camera found. Vision will be disabled.")
            self.cap = None
            return

        # set resolusi
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def _open_camera(self, index: int):
        try:
            if self.is_windows:
                cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(index)
            if cap.isOpened():
                return cap
        except Exception as e:
            logger.warning("Failed to open camera index %s: %s", index, e)
        return None

    def frames(self) -> Iterator[Tuple[bool, Optional["cv2.Mat"]]]:
        if self.cap is None:
            while True:
                yield False, None  # kamera tidak ada
        else:
            while True:
                if not self.cap.isOpened():
                    logger.error("❌ Camera unexpectedly closed")
                    break

                ret, frame = self.cap.read()
                if not ret or frame is None:
                    logger.warning("⚠️ Empty frame from camera")
                    continue

                yield ret, frame

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            logger.info("📷 Camera released")

    def __del__(self):
        self.release()