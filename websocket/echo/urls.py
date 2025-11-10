from django.urls import path

from echo.views import *

app_name = 'echo'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('echo-image', EchoImageView.as_view(), name='echo_image'),
    path('chat/<str:user>/', ChatView.as_view(), name='chat'),
    path('chat/new/<str:user>/', NewMessage.as_view(), name='chat'),
]
