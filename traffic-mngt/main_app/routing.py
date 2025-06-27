from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/alerts/', consumers.AlertConsumer.as_asgi()),
]
