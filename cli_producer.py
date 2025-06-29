from quixstreams import Application
from message.message import MessageBuilder
def main():

    app_producer = Application(broker_address="localhost:9092", loglevel="DEBUG")


    with app_producer.get_producer() as producer:
        while True:
            input("Enviar mensaje de prueba: \n")
            tema = "Mensaje de prueba"
            message_builder = MessageBuilder(tema)
            message = (message_builder.add_personaje("Homero Simpson").add_script("Este es un mensaje de prueba.").add_pth_voice("HOMERO SIMPSON LATINO").build())
            producer.produce(
                topic="scripts_video", key="temas_input_humano", value=str(message.to_dict())
            )


if __name__ == "__main__":
    main()
