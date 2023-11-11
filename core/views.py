import json
import pika
import os


from rest_framework import viewsets, status, exceptions
from rest_framework.response import Response

from core.models import VideoFile
from core.serializers import VideoSerializer


connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host='localhost'
    )
)
channel = connection.channel()


class VideoViewset(viewsets.ModelViewSet):
    queryset = VideoFile.objects.all()
    serializer_class = VideoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = VideoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        video = serializer.save(video_data=data.get('video').file.read())

        message = {
            'video_id': str(video.pk),
            'audio_id': None,
            'email': 'joeledmond95@yahoo.com'
        }

        try:
            channel.queue_declare(queue='video', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key='video',
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
            )
            channel.close()
        except Exception as err:
            print(err)
            # instance = get_object_or_404(VideoFile, pk=video.pk)
            # instance.delete()
            self.perform_destroy(video)
            raise exceptions.APIException("Internal server error")

        os.remove(str(video.video))
        return Response(serializer.data, status=status.HTTP_201_CREATED)
