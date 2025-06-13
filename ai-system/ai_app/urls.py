from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter, SimpleRouter


router = DefaultRouter()
router.register(r'camera_stream', views.CameraStreamViewSet, basename='camera_stream')

urlpatterns = [
    path('', include(router.urls)),
]
