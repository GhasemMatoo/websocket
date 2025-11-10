import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.utils.safestring import mark_safe
from django.shortcuts import render, HttpResponse
from django.views import View


# Create your views here.
class IndexView(View):
    template_name = "../templates/echo/index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class EchoImageView(View):
    template_name = "../templates/echo/echo-image.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class ChatView(View):
    template_name = "../templates/echo/join_chat.html"

    def get(self, request, *args, **kwargs):
        context = {'username_json': mark_safe(json.dumps(kwargs.get("user")))}
        return render(request, self.template_name, context=context)


class NewMessage(View):

    def get(self, request, *args, **kwargs):
        text = request.GET["text"]
        receiver = request.GET["receiver"]
        username = kwargs.get("user")
        channel_layer = get_channel_layer('default')
        group_name = F'chat_{receiver}'
        context = json.dumps({"sender": username, "receiver": receiver, "text": text})
        async_to_sync(channel_layer.group_send)(
            group_name, {"type": "chat_message", "message": context})
        return HttpResponse(context)
