import json
import pika
import os
import tempfile
import moviepy.editor

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.mail import send_mail

from rest_framework import viewsets, status, exceptions
from rest_framework.response import Response

from core.models import AudioFile, VideoFile
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


def video_from_db(video_id):
    video = get_object_or_404(VideoFile, pk=video_id)
    return video


def start_convert(ch, message):
    video_id = message.get('video_id')
    video_instance = video_from_db(video_id)
    tf = tempfile.NamedTemporaryFile()
    tf.write(video_instance.video_data)

    audio = moviepy.editor.VideoFileClip(tf.name).audio
    audio_path = f"{str(video_instance.video)[:-4]}_proxidev.mp3"
    audio.write_audiofile(audio_path)
    tf.close()

    f = open(audio_path, 'rb')
    data = f.read()
    audio = AudioFile.objects.create(
        audio=data
    )
    f.close()

    message['audio_id'] = str(audio.pk)
    try:
        ch.basic_publish(
            exchange="",
            routing_key="audio",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )
        os.remove(str(audio_path))
    except Exception as err:
        print(err)
        audio = get_object_or_404(AudioFile, pk=audio.pk)
        audio.delete()
        os.remove(str(audio_path))
        return "Error"


def sent_notification(message):
    email_from = settings.EMAIL_HOST
    email_to = message['email']
    subject = f"Your video f n.{message['audio_id']} has converted"
    body = f"""
        Dear {email_to},

        You download link is:
        http://localhost:8000/api/v1/audio/{message['audio_id']}/

        Thank
    """

    try:
        send_mail(
            subject=subject,
            from_email=email_from,
            message=body,
            recipient_list=[email_to],
            fail_silently=True
        )
        print("[*] Email wast send successfuly")
    except Exception as err:
        print(err)
        return "error"
