import json

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
