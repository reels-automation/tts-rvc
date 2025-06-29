import re
from abc import ABC

class ITtsGenerator(ABC):
    """
    Interface for the TTS strategy pattern generator
    """

    def sanitize_filename(self, filename: str) -> str:
        """Sanitizes a filename
        """
        filename = re.sub(r'[\/:*?"<>|]', "_", filename)
        filename = filename.replace(" ", "_")  
        filename = filename.replace("..", "_")  
        filename = filename.replace(".", "_")  
        return filename

    
    def generate_tts(self, script:str, tema:str):
        """Generates a tts given a script and a topic

        Args:
            script (str): El script para procesar el tts
            tema (str): El tema sobre lo que se trata el script. Para ponerle nombre
        """
        pass