from django.urls import path
from chat import views

app_name = 'chat'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.CreateChatView.as_view(), name='create_chat'),
    path('<str:chat_id>/', views.chat, name='chat'),
    path('<str:chat_id>/leave/', views.leave_chat, name='leave_chat'),
]