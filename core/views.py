from django.shortcuts import render
from rest_framework import viewsets

from core.models import VideoFile
from core.serializers import VideoSerializer


class VideoViewset(viewsets.ModelViewSet):
    queryset = VideoFile.objects.all()
    serializer_class = VideoSerializer
