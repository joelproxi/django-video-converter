import json
import pika
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'config.settings')
django.setup()


connection = pika.BlockingConnection(
    parameters=pika.ConnectionParameters(
        host='localhost'
    )
)
channel = connection.channel()


def main():
    from core.views import start_convert

    def callback(ch, method, properties, body):
        print(f' [*] -> received {body.decode()}')
        message = json.loads(body.decode())
        err = start_convert(ch, message)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        print("[x] Done")

    channel.basic_consume(queue='video', on_message_callback=callback)
    print(' [x] -> Waitting form message, press CTL+C to quit  ')
    channel.start_consuming()


main()