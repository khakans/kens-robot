from ultralytics import YOLO
import cv2
import os

class Scene:
    def __init__(self, model_path="models/yolov8n.pt"):
        if not os.path.exists(model_path) and model_path == "models/yolov8n.pt":
            print("[Warning] Model path not found, using default pretrained YOLO")
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            raise RuntimeError(f"❌ Failed to load YOLO model {model_path}: {e}")

    def detect(self, frame):
        if frame is None:
            return None, []

        try:
            results = self.model(frame, verbose=False)
        except Exception as e:
            print(f"[Error] YOLO inference failed: {e}")
            return frame, []

        objects = []
        for r in results:
            if not hasattr(r, "boxes") or r.boxes is None:
                continue

            for box in r.boxes:
                try:
                    cls = int(box.cls[0])
                    label = r.names.get(cls, str(cls))
                    conf = float(box.conf[0])
                    objects.append({"label": label, "confidence": conf})

                    # draw box safely
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    x1, y1 = max(0, x1), max(0, y1)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        f"{label} {conf:.2f}",
                        (x1, max(10, y1 - 5)),  # cegah negatif
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )
                except Exception as e:
                    print(f"[Warning] Skipped box due to error: {e}")
                    continue

        return frame, objects
