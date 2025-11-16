from django.urls import path
from chat import views

app_name = 'chat'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('create/', views.CreateChatView.as_view(), name='create_chat'),
    path('<str:chat_id>/', views.ChatView.as_view(), name='chat'),
    path('<str:chat_id>/leave/', views.LeaveChatView.as_view(), name='leave_chat'),
]