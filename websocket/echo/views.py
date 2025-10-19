from django.shortcuts import render, HttpResponse
from django.views import View


# Create your views here.
class IndexView(View):
    def get(self, request):
        return HttpResponse('Hello World')
