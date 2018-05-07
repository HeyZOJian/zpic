from channels.generic.websocket import AsyncWebsocketConsumer
import json
from . import utils as websocket_utils
from channels.layers import get_channel_layer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # save user channels_name
        print("connent...")
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'chat_'+self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json['message']
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': text_data_json
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        print(event)
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class NoticeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("connect...")
        user_id = self.scope['url_route']['kwargs']['user_id']
        websocket_utils.channels_add(self.channel_name, user_id)
        await self.accept()

    async def disconnect(self, close_code):
        # websocket_utils.channels_remove(self.channel_name)
        print(self.channel_name)

    # Receive message from websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(">>>>>>>>>>>>>message from websocket: ", text_data_json)
        # message = text_data_json['message']
        # # Send message to room group
        # await self.channel_layer.group_send(
        #     self.room_group_name,
        #     {
        #         'type': 'chat_message',
        #         'message': text_data_json
        #     }
        # )

    # Receive message from channels
    async def notice_message(self, event):
        print(">>>>>>>>>>>>>message from channels: ", event)
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'notice_type' : event['notice_type'],
            'message': event['message']
        }))
