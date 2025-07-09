class TtsError(Exception):

    def __init__(self, mensaje, error_log, status_code,):
        
        self.mensaje = mensaje
        self.error_log = error_log
        self.status_code = status_code

    def __str__(self):
        return f"\n [TTS RVC ] \n Message:{self.mensaje} \n Status:{self.status_code} \n Log:{self.error_log} \n"