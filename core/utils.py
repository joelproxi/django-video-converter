import pika


connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost'
    )
)
channel = connection.channel()
