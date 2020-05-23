import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import asyncio

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        print(self);
        self.user = self.scope["user"]
        self.time = datetime.now()
        self.x = 0
        self.y = 0
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        asyncio.create_task(self.start_periodic_task())
        # while True:
        #     DURATION = 5000e-3
        #     await asyncio.sleep(DURATION)
        #     await self.send(text_data=json.dumps({
        #         'x': self.x,
        #         'y': self.y,
        #         'user':self.user.id
        #     }))

    async def start_periodic_task(self):
        while True:
            self.time = datetime.now()
            message = f"{self.x} {self.y} {self.user}"
            await self.send(text_data=json.dumps({
                'message': message,
                'x': self.x,
                'y': self.y,
                'user':self.user.id
            }))
            await asyncio.sleep(0.1)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        # wysylaj czas z backendu i porownuj wczesniej zapisany timestamp aby obliczyc pozycje
        print(self.user, self.time)
        tim = self.time
        self.time = datetime.now()
        diff = self.time - tim
        diff = diff / timedelta(milliseconds=1)
        if message == 'right':
            self.x = self.x + (100*diff/1000)
        if message == 'left':
            self.x = self.x - (100*diff/1000)
        if message == 'down':
            self.y = self.y + (100*diff/1000)
        if message == 'up':
            self.y = self.y - (100*diff/1000)
        message = message + f"{self.user}, {self.time}, diff: {diff}, x: {self.x}, y: {self.y}, id: {self.user.id}"

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'x': self.x,
                'y': self.y,
                'user': self.user.id
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        x = event['x']
        y = event['y']
        user = event['user']
        
        # self.time = datetime.now()
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
                'message': message,
                'x': x,
                'y':y,
                'user':user
        }))