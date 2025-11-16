import json
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.urls import reverse
from chat.models import Member, GroupChat, VideoThread
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from django.contrib.auth import authenticate, login, logout
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from chat.forms import UserRegisterForm


class LoginView(FormView):
    form_class = AuthenticationForm
    template_name = 'chat/login.html'
    success_url = "/chat/"

    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        return redirect('chat:index')


#
# def register(request):
#     if request.method == 'POST':
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password2')
#
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('chat:index')
#
#             return redirect('login')
#     else:
#         form = UserRegisterForm()
#     return render(request, 'chat/register.html', {'form': form})
class RegisterFormView(FormView):
    template_name = 'chat/register.html'
    form_class = UserRegisterForm
    success_url = "/accounts/login/"

    def form_valid(self, form):
        valid_data = form.cleaned_data
        if valid_data.get("password1") != valid_data.get("password2"):
            raise ValueError("not match password")
        if User.objects.filter(username=valid_data.get("username")).exists():
            raise ValueError("is user exist")
        password = valid_data.pop("password1")
        valid_data.pop("password2")
        valid_data["password"] = password
        User.objects.create(**valid_data)
        return super().form_valid(form)


# @login_required
# def index(request):
#     current_user = request.user
#     return render(request, 'chat/index.html', {'members': current_user.member_set.all()})

class IndexView(LoginRequiredMixin, View):
    template_name = 'chat/index.html'

    def get(self, request, *args, **kwargs):
        current_user = request.user
        return render(request, self.template_name, context={'members': current_user.member_set.all()})


# @login_required
# def create_chat(request):
#     current_user = request.user
#     title = request.POST['group_name']
#     chat = GroupChat.objects.create(creator_id=current_user.id, title=title)
#     Member.objects.create(chat_id=chat.id, user_id=current_user.id)
#     return redirect(reverse('chat:chat', args=[chat.unique_code]))
class CreateChatView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        current_user = request.user
        title = request.POST['group_name']
        chat = GroupChat.objects.create(creator_id=current_user.id, title=title)
        Member.objects.create(chat_id=chat.id, user_id=current_user.id)
        return redirect(reverse('chat:chat', kwargs={'chat_id': chat.unique_code}))


# @login_required
# def chat(request, chat_id):
#     current_user = request.user
#     try:
#         chat = GroupChat.objects.get(unique_code=chat_id)
#     except GroupChat.DoesNotExist:
#         return render(request, 'chat/404.html')
#     if request.method == "GET":
#         if Member.objects.filter(chat_id=chat.id, user_id=current_user.id).count() == 0:
#             return render(request, 'chat/join_chat.html', {'chatObject': chat})
#
#         return render(request, 'chat/chat.html',
#                       {'chatObject': chat, 'chat_id_json': mark_safe(json.dumps(chat.unique_code))})
#     elif request.method == "POST":
#         Member.objects.create(chat_id=chat.id, user_id=current_user.id)
#
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f"chat_{chat.unique_code}",
#             {
#                 'type': 'chat_activity',
#                 'message': json.dumps({'type': "join", 'username': current_user.username})
#             }
#         )
#
#         return render(request, 'chat/chat.html',
#                       {'chatObject': chat, 'chat_id_json': mark_safe(json.dumps(chat.unique_code))})


class ChatView(LoginRequiredMixin, View):
    current_user = None
    chat = None

    def setup(self, request, *args, **kwargs):
        chat_id = kwargs.get("chat_id")
        self.current_user = request.user
        try:
            self.chat = GroupChat.objects.get(unique_code=chat_id)
        except GroupChat.DoesNotExist:
            return render(request, 'chat/404.html')
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if Member.objects.filter(chat_id=self.chat.id, user_id=self.current_user.id).count() == 0:
            return render(request, 'chat/join_chat.html', {'chatObject': self.chat})

        return render(request, 'chat/chat.html',
                      {'chatObject': self.chat, 'chat_id_json': mark_safe(json.dumps(self.chat.unique_code))})

    def post(self, request, *args, **kwargs):
        Member.objects.create(chat_id=self.chat.id, user_id=self.current_user.id)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{self.chat.unique_code}",
            {'type': 'chat_activity', 'message': json.dumps({'type': "join", 'username': self.current_user.username})})

        return render(request, 'chat/chat.html',
                      {'chatObject': self.chat, 'chat_id_json': mark_safe(json.dumps(self.chat.unique_code))})


#
# @login_required
# def leave_chat(request, chat_id):
#     current_user = request.user
#     try:
#         chat = GroupChat.objects.get(unique_code=chat_id)
#     except GroupChat.DoesNotExist:
#         return render(request, 'chat/404.html')
#
#     if chat.creator_id == current_user.id:
#         chat.delete()
#
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f"chat_{chat.unique_code}",
#             {
#                 'type': 'chat_activity',
#                 'message': json.dumps({'type': "delete"})
#             }
#         )
#
#     else:
#         Member.objects.filter(chat_id=chat.id, user_id=current_user.id).delete()
#
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f"chat_{chat.unique_code}",
#             {
#                 'type': 'chat_activity',
#                 'message': json.dumps({'type': "leave", 'username': current_user.username})
#             }
#         )
#
#     return redirect('chat:index')

class LeaveChatView(LoginRequiredMixin, View):
    current_user = None
    chat = None

    def setup(self, request, *args, **kwargs):
        chat_id = kwargs.get("chat_id")
        self.current_user = request.user
        try:
            self.chat = GroupChat.objects.get(unique_code=chat_id)
        except GroupChat.DoesNotExist:
            return render(request, 'chat/404.html')
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if self.chat.creator_id == self.current_user.id:
            self.chat.delete()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{self.chat.unique_code}",
                {'type': 'chat_activity', 'message': json.dumps({'type': "delete"})}
            )
        else:
            Member.objects.filter(chat_id=self.chat.id, user_id=self.current_user.id).delete()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{self.chat.unique_code}", {
                    'type': 'chat_activity',
                    'message': json.dumps({'type': "leave", 'username': self.current_user.username})})

        return redirect('chat:index')
