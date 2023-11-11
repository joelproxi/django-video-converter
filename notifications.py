import os
import django
import json

from core.utils import channel

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'config.settings')
django.setup()


def main():
    from notification.views import send_mail_to_user

    channel.queue_declare(queue='audio', durable=True)

    def callback(ch, method, properties, body):
        print(f"[x] Received message {body.decode()}")
        data = json.loads(body.decode())

        err = send_mail_to_user(ch, data)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[x] Done ")

    print(f"[x] Press CTR+C to quit")
    channel.basic_consume(queue='audio', on_message_callback=callback)
    channel.start_consuming()


main()
