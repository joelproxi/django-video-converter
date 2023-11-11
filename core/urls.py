from django.urls import path
from rest_framework.routers import DefaultRouter

from core import views


router = DefaultRouter()
router.register('videos', views.VideoViewset, basename='videos'),


urlpatterns = [
    path('audio/<id>/', views.download_audio,)
] + router.urls
