import os
import requests
import unicodedata
import re
from config import MODELS, ADMIN_API, MODELS_FOLDER
import urllib.request

def sanitize_attribute(attribute: str):
    """Sanitiza un input para que no contenga caracteres que no puedan ser parseados

    Args:
        attribute (str):

    Returns:
        (str):
    """
    if attribute is not None:
        result = (
            unicodedata.normalize("NFKD", attribute)
            .encode("ASCII", "ignore")
            .decode("ASCII")
        )
        # Modify the regex to exclude dots
        result = re.sub(r"[^a-zA-Z0-9._-]", " ", result)
        result = result.strip()
        return result
    return None

def download_model(personaje:str, idioma:str):
    try:
        url_pth = f"{ADMIN_API}/get-voice-model-pth/{personaje}/{idioma}"
        url_index = f"{ADMIN_API}/get-voice-model-index/{personaje}/{idioma}"
        if not os.path.exists(f"{MODELS_FOLDER}/{personaje}"):
            os.makedirs(f"{MODELS_FOLDER}/{personaje}")
        
        file_pth_response = requests.get(url_pth)
        file_pth_data = file_pth_response.json()
        file_pth_namefile = file_pth_data["name"]
        file_pth_url = file_pth_data["url"]
        file_pth_path = os.path.join(MODELS_FOLDER, personaje, file_pth_namefile)

        url_pth_response = requests.get(file_pth_url)
        
        file_index_response = requests.get(url_index)
        file_index_data = file_index_response.json()
        file_index_namefile = file_index_data["name"]
        file_index_url = file_index_data["url"]
        url_index_response = requests.get(file_index_url)
        
        
        file_index_path = os.path.join(MODELS_FOLDER, personaje, file_index_namefile)
        
        with open(file_pth_path, "wb") as f:
            f.write(url_pth_response.content)

        with open(file_index_path, "wb") as f:
            f.write(url_index_response.content)
        

    except Exception as error:
        print(f"Unexpected error, couldn't donwload model: {personaje} ", error)

def download_all_models():
    print("Started to download models")
    try:
        url = f"{ADMIN_API}"
        modelos = requests.get(url).json()

        for modelo in modelos:
            print("modelo: ", modelo)
            personaje = modelo["personaje"]
            idioma = modelo["idioma"]
            download_model(personaje,idioma)
    except Exception as error:
        print("Unexpected error trying to download all models: ", error)

def donwload_rmvpe():
    rmvpe_path = 'rvc/models/predictors/rmvpe.pt'
    if not os.path.exists(rmvpe_path):
        print("Downloading RMVPE model...")
        os.makedirs(os.path.dirname(rmvpe_path), exist_ok=True)
        urllib.request.urlretrieve(
            'https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/rmvpe.pt',
            rmvpe_path
        )
