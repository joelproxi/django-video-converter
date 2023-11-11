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
    from core.views import sent_notification

    channel.queue_declare(queue='audio', durable=True)

    def callback(ch, method, properties, body):
        print(f" [*] Received {body.decode()}")
        message = json.loads(body.decode())

        err = sent_notification(message)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        print(" [x] Done ")

    print(' [x] -> Waitting form message, press CTL+C to quit  ')
    channel.basic_consume(queue='audio', on_message_callback=callback)
    channel.start_consuming()


main()