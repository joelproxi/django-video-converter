from rest_framework.routers import DefaultRouter

from core import views


router = DefaultRouter()
router.register('videos', views.VideoViewset, basename='videos'),

urlpatterns = router.urls
