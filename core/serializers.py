from rest_framework import serializers

from core.models import VideoFile


class VideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoFile
        fields = ('id', 'video', 'video_data')
        extra_kwargs = {
            'video': {'write_only': True}
        }
