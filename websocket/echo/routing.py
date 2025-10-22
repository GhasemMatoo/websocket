from django.urls import path
from echo import consumers

websocket_urlpatterns = [
    path('ws/', consumers.EchoConsumer.as_asgi()),
    path('ws/echo-image/', consumers.EchoImages.as_asgi()),
]
