from channels.generic.websocket import AsyncWebsocketConsumer
import json
from . import utils as websocket_utils
from channels.layers import get_channel_layer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # TODO： 拿离线消息并删除
        # save user channels_name
        print("connent in "+self.scope['url_route']['kwargs']['room_id']+"...")
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = 'chat_'+self.room_name
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        for message in websocket_utils.get_all_offline_chat_message(self.room_name):
            print(">>>offlinemsg:",message)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat.message',
                    'message': message
                }
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
        print(">>>>>text_data",text_data_json)
        print(">>>>>room_name:",self.room_name)
        user_id = text_data_json['friend_id']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': text_data_json
            }
        )
        if not websocket_utils.is_online(user_id):
            print(">>>>offline")
            websocket_utils.add_offline_chat_message(self.room_name, text_data_json)



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
        # TODO: 获取离线通知和消息

        user_id = self.scope['url_route']['kwargs']['user_id']
        websocket_utils.channels_add(self.channel_name, user_id)
        await self.accept()

    async def disconnect(self, close_code):
        user_id = self.scope['url_route']['kwargs']['user_id']
        websocket_utils.channels_remove(user_id)


    # Receive message from websocket
    async def receive(self, data):
        data = json.loads(data)
        print(">>>>>>>>>>>>>message from websocket: ", data)


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
