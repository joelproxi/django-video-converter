from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response

from core.models import VideoFile
from core.serializers import VideoSerializer


class VideoViewset(viewsets.ModelViewSet):
    queryset = VideoFile.objects.all()
    serializer_class = VideoSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = VideoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(video_data=data.get('video').file.read())
        return Response(serializer.data, status=status.HTTP_201_CREATED)
