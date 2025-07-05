import time
import os
import ast
import shutil
import logging
from minio import Minio
from dotenv import load_dotenv  
from minio.error import S3Error
from tts.rvc_tts import RvcTTS
from quixstreams import Application
from message.message import MessageBuilder
from config import TEMP_TXT, TEMP_TTS_AUDIOS, KAFKA_BROKER,MINIO_ACCESS_KEY,MINIO_ADDRESS,MINIO_SECRET_KEY
from utils import download_all_models, donwload_rmvpe, create_boilerplate_folders

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
    
    
    create_boilerplate_folders()
    download_all_models()
    donwload_rmvpe()

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
                    try:
                    
                        msg = consumer.poll(10)
                        if msg is None:
                            print("Waiting...")
                        elif msg.error() is not None:
                            raise ValueError(msg.error())
                        else:
                            msg_value = msg.value()
                            consumer.store_offsets(msg)
                            msg_value_json_response = ast.literal_eval(msg_value.decode("utf-8"))
                            
                            print("msg value", msg_value_json_response)
                            script = msg_value_json_response["script"]
                            
                            tema = msg_value_json_response["tema"]
                            tts_voice = msg_value_json_response["audio_item"][0]["tts_voice"]
                            pitch = msg_value_json_response["audio_item"][0]["pitch"]
                            pth_voice = msg_value_json_response["audio_item"][0]["pth_voice"]
                            
                            full_audio_name_path, audio_name = current_tts.generate_tts(script,tts_voice,pth_voice, pitch,tema)
                            new_audio_path = full_audio_name_path
                            bucket_name = "audios-tts"
                            destination_file = full_audio_name_path

                            audio_item_save = [{
                                "tts_audio_name": audio_name,
                                "tts_audio_directory": bucket_name,
                                "file_getter":"minio",
                                "pitch": msg_value_json_response["audio_item"][0]["pitch"],
                                "tts_voice": msg_value_json_response["audio_item"][0]["tts_voice"],
                                "tts_rate": msg_value_json_response["audio_item"][0]["tts_rate"],
                                "pth_voice": msg_value_json_response["audio_item"][0]["pth_voice"],
                            }]

                            destination_file = os.path.basename(new_audio_path)
                            minio_client.fput_object(
                                bucket_name, destination_file, new_audio_path
                            )
                            print(
                                f"{new_audio_path}, succesfully uploaded as object: {destination_file}, to bucket: {bucket_name}"
                            )
                            os.remove(new_audio_path)

                            app_producer = Application(
                                broker_address=KAFKA_BROKER, loglevel="DEBUG"
                            )
                            with app_producer.get_producer() as producer:

                                print("MESSAGE VAUE: ", msg_value)
                                print("MESSAGE VAUE 2: ", msg_value)

                                message_builder = MessageBuilder(msg_value_json_response["tema"])
                                message = (message_builder
                                    .add_usuario(msg_value_json_response["usuario"])
                                    .add_idioma(msg_value_json_response["idioma"])
                                    .add_personaje(msg_value_json_response["personaje"])
                                    .add_script(msg_value_json_response["script"])
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
                                    key = "Ai Subtitles",
                                    value = str(message.to_dict())
                                )
                                print("Produced. Closing Producer")
                    except ValueError as ex:
                        print(f"Error in consuming message: {ex}. Recreating consumer...")
                        consumer = create_consumer(KAFKA_BROKER)  # Recreate consumer on error
                        break
                    except ArithmeticError as ex:
                        print(f"Unexpected error: {ex}. Retrying...")
                        time.sleep(5)  # Retry after waiting a bit
                        break
        except ArithmeticError as e:
            print(f"Failed to initialize consumer: {e}. Retrying...")
            time.sleep(5)  # Wait before trying again

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except S3Error as ex:
        print(f"Ocurrió un error con S3 bucekt: {ex}")
