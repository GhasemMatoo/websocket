import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class EchoConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data=text_data)


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


class Chat(WebsocketConsumer):
    user_id = None
    group_name = None

    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']["username"]
        self.group_name = f'chat_{self.user_id}'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None):
        if text_data is not None:
            text_data_json = json.loads(text_data)
            user_name = text_data_json['receiver']
            user_group_name = f'chat_{user_name}'
            async_to_sync(self.channel_layer.group_send)(
                user_group_name, {'type': 'chat_message', 'message': text_data})

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=message)
