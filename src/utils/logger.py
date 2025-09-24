import logging
import os

# Pastikan folder logs ada
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "robot.log")

# Konfigurasi logging global
logging.basicConfig(
    level=logging.DEBUG,  # simpan semua level ke file
    format="[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),               # tampilkan ke console
        logging.FileHandler(LOG_FILE, "a")     # simpan ke logs/robot.log
    ]
)

# Ambil logger utama
logger = logging.getLogger("robot")

def get_logger(name: str = None):
    """Ambil child logger. Jika name None, return logger utama."""
    return logger.getChild(name) if name else logger
