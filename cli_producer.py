from quixstreams import Application
from message.message import MessageBuilder

def main():

    app_producer = Application(broker_address="localhost:9092", loglevel="DEBUG")

    with app_producer.get_producer() as producer:
        while True:
            
            tema="Video De prueba"
            idioma="es"
            personaje="Homero Simpson"
            usuario="43eda5b3-1c2b-424b-b460-c4d49198fc99"
            script="Holy Molly"
            audio_item=[{'tts_audio_name': '', 'tts_audio_directory': '', 'file_getter': '', 'pitch': 0, 'tts_voice': 'es-ES-XimenaNeural', 'tts_rate': 0, 'pth_voice': 'homero'}]
            print(audio_item[0]["pth_voice"])
            subtitle_item=""
            author=""
            gameplay_name="subway.mp4"
            background_music=""
            images=""
            random_images="True"
            random_amount_images="1"
            add_gpt_model="llama3.2:3b"
            input("Procesar un nuevo video: \n")
            message_builder = MessageBuilder(tema)
            message = (message_builder.add_personaje(personaje)
                       .add_idioma(idioma)
                       .add_script(script)
                       .add_usuario(usuario)
                       .add_audio_item(audio_item)
                       .add_subtitle_item(subtitle_item)
                       .add_author(author)
                       .add_gameplay_name(gameplay_name)
                       .add_background_music(background_music)
                       .add_images(images)
                       .add_random_images(random_images)
                       .add_random_amount_images(random_amount_images)
                       .add_gpt_model(add_gpt_model)
                       .build()) 

            print(message.to_dict())

            producer.produce(
                topic="scripts_video", key="temas_input_humano", value=str(message.to_dict())
            )

if __name__ == "__main__":
    main()