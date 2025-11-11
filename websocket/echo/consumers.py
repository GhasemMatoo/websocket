import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer


class EchoConsumer(WebsocketConsumer):
    group_name = None
    user = None

    def connect(self):
        self.group_name = "echo_1"
        self.user = self.scope.get("user", False)
        if self.user and self.user.is_active:
            async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
            self.accept()
        else:
            self.close(403)

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data=text_data)

    def send_echo_message(self, event):
        message = event['message']
        self.send(text_data=message)


class EchoImages(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            self.send(text_data=text_data)
        if bytes_data is not None:
            self.send(bytes_data=bytes_data)


class Chat(AsyncWebsocketConsumer):
    user_id = None
    group_name = None

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']["username"]
        self.group_name = f'chat_{self.user_id}'
        # async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name) 
        await self.channel_layer.group_add(self.group_name, self.channel_name)  # update: async
        await self.accept()

    async def disconnect(self, close_code):
        # async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)  # update: async

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            text_data_json = json.loads(text_data)
            user_name = text_data_json['receiver']
            user_group_name = f'chat_{user_name}'
            # async_to_sync(self.channel_layer.group_send)(
            #     user_group_name, {'type': 'chat_message', 'message': text_data})
            await self.channel_layer.group_send(
                user_group_name, {'type': 'chat_message', 'message': text_data})  # update: async
            await self.channel_layer.group_send("echo_1", {'type': 'send_echo_message', 'message': text_data})

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=message)
