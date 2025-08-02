import os
import shutil
import logging
import subprocess
import datetime
from errors.errors import TtsError
from tts.I_tts_generator import ITtsGenerator
from config import MODELS, TEMP_TTS_AUDIOS, TEMP_TXT, ADMIN_API, MODELS_FOLDER
from errors.errors import TtsError
import requests

class RvcTTS(ITtsGenerator):

    def generate_tts(self, script:str, tts_voice: str, ai_model_name: str, pitch: str, tema:str=None) -> str:
        try:
            if tema is not None:
                audio_name = f"{tema}_{datetime.datetime.now()}"
            else:
                audio_name = f"{datetime.datetime.now()}"
            
            audio_name = self.sanitize_filename(audio_name)
            audio_name = audio_name + ".mp3"
            
            print(f"Empezando a producir: {audio_name}")
            
            with open(TEMP_TXT, "w") as f:
                f.write(script)

            full_audio_path = f"{TEMP_TTS_AUDIOS}/{audio_name}"

            if len(tts_voice) == 0:
                tts_voice =  "es-MX-JorgeNeural"
            
            # Aquí hacemos el fetch a ADMIN_API para obtener modelos dinámicamente
            response = requests.get(ADMIN_API, timeout=5)
            response.raise_for_status()
            modelos_json = response.json()  # Lista de dicts con "personaje" e "idioma"

            modelos = []
            for m in modelos_json:
                personaje = m["personaje"]
                idioma = m["idioma"]
                modelos.append({
                    "name": personaje,
                    "pth_path": f"{MODELS_FOLDER}/{personaje}/{personaje}_{idioma}.pth",
                    "index_path": f"{MODELS_FOLDER}/{personaje}/{personaje}_{idioma}.index"
                })

            # Buscar el modelo que coincide con ai_model_name
            pth_path = ""
            index_path = ""
            for model in modelos:
                if model["name"] == ai_model_name:
                    pth_path = model["pth_path"]
                    index_path = model["index_path"]
                    break
            
            # Si no se encuentra, usar el primero como fallback
            if len(pth_path) == 0 or len(index_path) == 0:
                pth_path = modelos[0]["pth_path"]
                index_path = modelos[0]["index_path"]

        except Exception as Ex:
            raise TtsError(mensaje="Error al generar el tts", status_code=500, error_log=Ex)

        # El resto de tu código sigue igual...
        command = [
            "python3", "rvc_cli.py", "tts",
            "--tts_text", script,
            "--tts_file", TEMP_TXT,
            "--tts_voice", tts_voice,
            "--tts_rate", "0",
            "--output_tts_path", f"{TEMP_TTS_AUDIOS}/tts_output.wav",
            "--output_rvc_path", full_audio_path,
            "--pth_path", pth_path,
            "--index_path", index_path,
            "--pitch", str(pitch),
        ]

        try:
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise TtsError(
                    mensaje="Error al ejecutar el script TTS",
                    status_code=500,
                    error_log=result.stderr
                )
            print("XD: ", result.stderr)
            print("DOU: ", result.stdout)

        except Exception as ex:
            raise TtsError(mensaje=f"Error al ejecutar el raw script de TTS", status_code=500, error_log=ex)

        logging.info("Video creado correctamente: \n %s", result.stdout)
        return full_audio_path, audio_name
