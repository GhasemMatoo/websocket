from django.shortcuts import render, HttpResponse
from django.views import View


# Create your views here.
class IndexView(View):
    template_name = "../templates/echo/index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
