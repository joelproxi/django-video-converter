from rest_framework import serializers

from .models import AudioFile, VideoFile


class VideoFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoFile
        fields = ('id', 'video', 'video_data')
        extra_kwargs = {
            'video': {'write_only': True}
        }


class AudioSerializer(serializers.ModelSerializer):

    class Meta:
        model = AudioFile
        fields = '__all__'
