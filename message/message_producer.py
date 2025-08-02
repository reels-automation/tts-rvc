import os
import ast
import logging
from minio import Minio
from quixstreams import Application
from config import KAFKA_BROKER
from message.message import MessageBuilder
from errors.errors import TtsError
from tts.I_tts_generator import ITtsGenerator


def produce_message(
    msg: str, consumer, minio_client: ITtsGenerator, current_tts: ITtsGenerator
):
    """Parses and produces a message to kafka broker

    Args:
        msg (str): The message polled from a kafka microservice
    """
    try:
        msg_value = msg.value()
        consumer.store_offsets(msg)
        msg_value_json_response = ast.literal_eval(msg_value.decode("utf-8"))
        script = msg_value_json_response["script"]
        tema = msg_value_json_response["tema"]
        tts_voice = msg_value_json_response["audio_item"][0]["tts_voice"]
        pitch = msg_value_json_response["audio_item"][0]["pitch"]
        pth_voice = msg_value_json_response["audio_item"][0]["pth_voice"]
        full_audio_name_path, audio_name = current_tts.generate_tts(
            script, tts_voice, pth_voice, pitch, tema
        )
        new_audio_path = full_audio_name_path
        bucket_name = "audios-tts"
        destination_file = full_audio_name_path
        audio_item_save = [
            {
                "tts_audio_name": audio_name,
                "tts_audio_directory": bucket_name,
                "file_getter": "minio",
                "pitch": msg_value_json_response["audio_item"][0]["pitch"],
                "tts_voice": msg_value_json_response["audio_item"][0]["tts_voice"],
                "tts_rate": msg_value_json_response["audio_item"][0]["tts_rate"],
                "pth_voice": msg_value_json_response["audio_item"][0]["pth_voice"],
            }
        ]
        destination_file = os.path.basename(new_audio_path)
        minio_client.fput_object(bucket_name, destination_file, new_audio_path)
        logging.info(
            f"{new_audio_path}, succesfully uploaded as object: {destination_file}, to bucket: {bucket_name}"
        )
        os.remove(new_audio_path)
        app_producer = Application(broker_address=KAFKA_BROKER, loglevel="DEBUG")
        with app_producer.get_producer() as producer:
            message_builder = MessageBuilder(msg_value_json_response["tema"])
            message = (
                message_builder.add_usuario(msg_value_json_response["usuario"])
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
                .add_random_amount_images(
                    msg_value_json_response["random_amount_images"]
                )
                .add_gpt_model(msg_value_json_response["gpt_model"])
                .build()
            )

            producer.produce(
                topic="audio_subtitles",
                key="Ai Subtitles",
                value=str(message.to_dict()),
            )
    except Exception as ex:
        raise TtsError(
            mensaje="Error al producir un mensaje", status_code=500, error_log=ex
        )
