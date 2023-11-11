from rest_framework.routers import DefaultRouter

from . import views


routeur = DefaultRouter()
routeur.register('', views.VideoViewset, basename='vidoes')

urlpatterns = routeur.urls
