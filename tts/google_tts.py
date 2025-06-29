import os
import shutil
import datetime
from tts.I_tts_generator import ITtsGenerator
from gtts import gTTS

class GoogleTts(ITtsGenerator):

    

    def generate_tts(self, script:str, tema:str=None) -> str :

        language = 'es'
        audio_gtts = gTTS(text=script, lang=language, slow=False)
        
        if tema is not None:
            audio_name = f"{tema}_{datetime.datetime.now()}.mp3"
        else:
            audio_name = f"{datetime.datetime.now()}.mp3"
        audio_name = self.sanitize_filename(audio_name)
        audio_gtts.save(audio_name)
    
        return audio_name