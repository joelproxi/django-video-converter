import io
import json
import os
import tempfile
import moviepy.editor
import pika

from django.shortcuts import get_object_or_404
from django.http.response import FileResponse

from rest_framework import viewsets, exceptions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from .models import AudioFile, VideoFile
from .serializers import VideoFileSerializer
from .utils import channel


channel = channel


class VideoViewset(viewsets.ModelViewSet):
    queryset = VideoFile.objects.all()
    serializer_class = VideoFileSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        video = data.get('video')
        serializer = VideoFileSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(video_data=video.file.read())

        message = {
            "video_id": str(instance.id),
            'audio_id': None,
            'email': 'joeledmond95@yahoo.com'
        }

        try:
            channel.queue_declare(queue='video', durable=True)
            channel.basic_publish(
                exchange='',
                routing_key='video',
                body=json.dumps(message)
            )
        except Exception as err:
            print(err)
            self.perform_destroy(instance)
            raise exceptions.APIException("Internal server error")
        os.remove(str(instance.video))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


def get_video_from_db(video_id):
    video = get_object_or_404(VideoFile, id=video_id)
    return video


def start_convert(ch, message):
    tf = tempfile.NamedTemporaryFile()
    video_id = message['video_id']
    video = get_video_from_db(video_id)
    tf.write(video.video_data)

    print("start conversion")
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()

    audio_path = f"{str(video.video)[:-4]}_proxidev.mp3"
    audio.write_audiofile(audio_path)

    f = open(audio_path, 'rb')
    data = f.read()
    audio = AudioFile.objects.create(audio_data=data)
    f.close()

    message['audio_id'] = str(audio.pk)

    try:
        ch.queue_declare('audio', durable=True)
        ch.basic_publish(
            exchange='',
            routing_key='audio',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            )
        )

    except Exception as err:
        print(err)
        try:
            data = AudioFile.objects.get(id=audio.pk)
            data.delete()
        except AudioFile.DoesNotExist:
            raise exceptions.APIException("Internal server error")
        return "Error"
    # os.remove(audio_path)


@api_view(['GET'])
def download_audio(request, id):
    audio = get_object_or_404(AudioFile, pk=id)
    buffer = io.BytesIO(audio.audio_data)
    buffer.seek(0)
    response = FileResponse(
        buffer,
        as_attachment=True,
        filename=f"proxidev_{str(audio.pk)}.mp3"
    )
    return response