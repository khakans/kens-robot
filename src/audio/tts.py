# src/audio/tts.py
from gtts import gTTS
import tempfile
import os
import subprocess
import platform

class TTS:
    def say(self, text, lang="id"):
        mp3_file = None
        try:
            # Buat file temp mp3
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                mp3_file = fp.name

            # Generate TTS (mp3)
            tts = gTTS(text=text, lang=lang)
            tts.save(mp3_file)

            # Mainkan mp3
            if platform.system() == "Darwin":
                # MacOS pakai afplay
                subprocess.run(["afplay", mp3_file])
            elif platform.system() == "Windows":
                # Windows pakai start / miniplayer
                subprocess.run(["powershell", "-c", f"(New-Object Media.SoundPlayer '{mp3_file}').PlaySync();"])
            else:
                # Linux pakai mpg123 / mpv (pastikan terinstall)
                subprocess.run(["mpg123", mp3_file])

        except Exception as e:
            print(f"[Error] TTS gagal: {e}")

        finally:
            # Bersihkan file temp
            if mp3_file and os.path.exists(mp3_file):
                try:
                    os.remove(mp3_file)
                except Exception as e:
                    print(f"[WARN] Gagal hapus file {mp3_file}: {e}")
