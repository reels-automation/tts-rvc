import os
from dotenv import load_dotenv
load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_FOLDER = os.path.join(BASE_DIR, "models")
ADMIN_API = os.getenv("ADMIN_API")
TEMP_TTS_AUDIOS = "temp_tts_audios"
TEMP_TXT = "temp_tts_text.txt"
MODELS = [{"name": "homero", "pth_path": f"{MODELS_FOLDER}/homero/homero_es.pth", "index_path":f"{MODELS_FOLDER}/homero/homero_es.index"},
          {"name": "peter_griffin", "pth_path": f"{MODELS_FOLDER}/peter_griffin/peter_griffin_es.pth", "index_path":f"{MODELS_FOLDER}/peter_griffin/peter_griffin_es.index"}]