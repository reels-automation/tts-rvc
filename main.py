import time
import os
import ast
import logging
from minio import Minio
from dotenv import load_dotenv  
from tts.rvc_tts import RvcTTS
from quixstreams import Application
from errors.errors import TtsError
from message.message import MessageBuilder
from message.message_producer import produce_message
from config import TEMP_TXT, TEMP_TTS_AUDIOS, KAFKA_BROKER,MINIO_ACCESS_KEY,MINIO_ADDRESS,MINIO_SECRET_KEY
from utils import setup
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
    
    setup()
    
    try:
        current_tts = RvcTTS()
        
        app_consumer = create_consumer(KAFKA_BROKER)

        minio_client = Minio(
        MINIO_ADDRESS,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False)
        
        while True:
            with app_consumer.get_consumer() as consumer:
                consumer.subscribe(["scripts_video"])
                while True:                    
                    msg = consumer.poll(10)
                    if msg is None:
                        print("Waiting...")
                    elif msg.error() is not None:
                        raise ValueError(msg.error())
                    else:
                        produce_message(msg,consumer,minio_client,current_tts)
    except TtsError as tts_err:
        logging.error(tts_err)
    except Exception: 
        logging.exception("Unhandled exception", exc_info=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
