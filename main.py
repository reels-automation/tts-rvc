import time
import os
import ast
import logging
from minio import Minio
from dotenv import load_dotenv  
from tts.rvc_tts import RvcTTS
from quixstreams import Application
from message.message import MessageBuilder
from config import TEMP_TXT, TEMP_TTS_AUDIOS, KAFKA_BROKER, MINIO_ACCESS_KEY, MINIO_ADDRESS, MINIO_SECRET_KEY
from utils import download_all_models, donwload_rmvpe, create_boilerplate_folders
from errors.errors import TtsError

load_dotenv()

def create_consumer(KAFKA_BROKER):
    return Application(
        broker_address=KAFKA_BROKER,
        loglevel="DEBUG",
        consumer_group="scripts_video_reader",
        auto_offset_reset="latest",
        consumer_poll_timeout=5000,
    )

def main():
    try:
        
        create_boilerplate_folders()
        download_all_models()
        donwload_rmvpe()
    except TtsError as ex:
        print(ex)
    except Exception as ex:
        print(ex)


    current_tts = RvcTTS()
    app_consumer = create_consumer(KAFKA_BROKER)
    minio_client = Minio(
        MINIO_ADDRESS,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )

    while True:
        try:
            with app_consumer.get_consumer() as consumer:
                consumer.subscribe(["scripts_video"])
                while True:
                    msg = consumer.poll(10)
                    if msg is None:
                        print("Waiting...")
                        continue

                    if msg.error() is not None:
                        logging.error(f"Consumer error: {msg.error()}")
                        continue

                    try:
                        msg_value = msg.value()
                        consumer.store_offsets(msg)
                        msg_value_json_response = ast.literal_eval(msg_value.decode("utf-8"))

                        print("msg value", msg_value_json_response)
                        script = msg_value_json_response["script"]
                        tema = msg_value_json_response["tema"]
                        tts_voice = msg_value_json_response["audio_item"][0]["tts_voice"]
                        pitch = msg_value_json_response["audio_item"][0]["pitch"]
                        pth_voice = msg_value_json_response["audio_item"][0]["pth_voice"]

                        full_audio_name_path, audio_name = current_tts.generate_tts(script, tts_voice, pth_voice, pitch, tema)
                        bucket_name = "audios-tts"
                        destination_file = os.path.basename(full_audio_name_path)

                        audio_item_save = [{
                            "tts_audio_name": audio_name,
                            "tts_audio_directory": bucket_name,
                            "file_getter": "minio",
                            "pitch": pitch,
                            "tts_voice": tts_voice,
                            "tts_rate": msg_value_json_response["audio_item"][0]["tts_rate"],
                            "pth_voice": pth_voice,
                        }]

                        minio_client.fput_object(bucket_name, destination_file, full_audio_name_path)
                        print(f"{full_audio_name_path} successfully uploaded as {destination_file} to bucket {bucket_name}")
                        os.remove(full_audio_name_path)

                        app_producer = Application(broker_address=KAFKA_BROKER, loglevel="DEBUG")
                        with app_producer.get_producer() as producer:
                            message_builder = MessageBuilder(tema)
                            message = (message_builder
                                       .add_usuario(msg_value_json_response["usuario"])
                                       .add_idioma(msg_value_json_response["idioma"])
                                       .add_personaje(msg_value_json_response["personaje"])
                                       .add_script(script)
                                       .add_audio_item(audio_item_save)
                                       .add_subtitle_item(msg_value_json_response["subtitle_item"])
                                       .add_author(msg_value_json_response["author"])
                                       .add_gameplay_name(msg_value_json_response["gameplay_name"])
                                       .add_background_music(msg_value_json_response["background_music"])
                                       .add_images(msg_value_json_response["images"])
                                       .add_random_images(msg_value_json_response["random_images"])
                                       .add_random_amount_images(msg_value_json_response["random_amount_images"])
                                       .add_gpt_model(msg_value_json_response["gpt_model"])
                                       .build()
                                      )

                            producer.produce(
                                topic="audio_subtitles",
                                key="Ai Subtitles",
                                value=str(message.to_dict())
                            )
                            print("Produced message successfully")

                    except TtsError as ex:
                        logging.error(f"TTS error: {ex}")
                    except Exception as ex:
                        logging.error(f"Unexpected error processing message: {ex}")

        except Exception as e:
            logging.error(f"Consumer context error: {e}. Restarting consumer loop after delay...")
            time.sleep(5)  # Espera antes de reintentar para no hacer loop rápido

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
