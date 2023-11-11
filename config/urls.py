
from django.contrib import admin
from django.urls import include, path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/audio/<id>/', views.download_audio),
    path('api/v1/videos/', include('core.urls')),
]
