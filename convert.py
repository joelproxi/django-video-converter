import os
import json
import django

from core.utils import channel

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'config.settings')
django.setup()


channel = channel


def main():
    from core.views import start_convert
    channel.queue_declare(queue='video', durable=True)

    def callback(ch, method, properties, body):
        print(f"[X] Received: {body.decode()}")
        message = json.loads(body.decode())

        err = start_convert(ch, message)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        print("[X] Done")

    print("[X] Press CLT+C to quit ")
    channel.basic_consume(queue='video', on_message_callback=callback)
    channel.start_consuming()


main()