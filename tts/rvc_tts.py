import os
import shutil
import subprocess
import datetime
from tts.I_tts_generator import ITtsGenerator
from config import MODELS, TEMP_TTS_AUDIOS, TEMP_TXT

class RvcTTS(ITtsGenerator):

    def generate_tts(self, script:str, tts_voice: str, ai_model_name: str, pitch: str, tema:str=None) -> str :
        
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
        
        pth_path = ""
        index_path = ""
        for model in MODELS:
            if model["name"] == ai_model_name:
                pth_path = model["pth_path"]
                index_path = model["index_path"]
        
        if len(pth_path) == 0  or len(index_path) == 0:
            pth_path = MODELS[0]["pth_path"]
            index_path = MODELS[0]["index_path"]
        
        print("pth_path ", pth_path)
        print("index_path ", index_path)

        print("full_audio_path", full_audio_path)

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
        result = subprocess.run(command, capture_output=True, text=True)
        print("result : ", result)
        if result.returncode == 0:
            print("TTS conversion successful!")
        else:
            print("Error:", result.stderr)
        
        return full_audio_path, audio_name