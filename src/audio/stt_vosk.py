import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer

class VoskSTT:
    def __init__(self, model_path: str, samplerate: int = 16000, device=None):
        self.q = queue.Queue()
        self.samplerate = samplerate
        self.device = device
        self.model = Model(model_path)
        self.stream = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[Audio Warning] {status}")  # hindari crash
        self.q.put(bytes(indata))

    def listen_once(self, timeout=10):
        rec = KaldiRecognizer(self.model, self.samplerate)
        text = ""

        try:
            with sd.RawInputStream(
                samplerate=self.samplerate,
                blocksize=8000,
                dtype="int16",
                channels=1,
                device=self.device,
                callback=self._callback,
            ):
                print("🎤 Listening ...")

                for _ in range(int(self.samplerate / 8000 * timeout)):
                    try:
                        data = self.q.get(timeout=1)  # biar nggak freeze
                    except queue.Empty:
                        continue

                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        text = res.get("text", "").strip()
                        if text:  # stop lebih cepat kalau ada hasil
                            break
                    else:
                        # ambil partial result
                        partial = json.loads(rec.PartialResult())
                        if partial.get("partial"):
                            print(f"(partial) {partial['partial']}")

        except Exception as e:
            print(f"[Error] STT failed: {e}")
            return None, None

        if text:
            return text, "en"  # sementara pakai bahasa Indonesia
        return None, None