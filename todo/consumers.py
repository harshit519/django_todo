import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Todo

class TodoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'todo_{self.room_name}'

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
        message_type = text_data_json.get('type', 'message')
        message = text_data_json.get('message', '')

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'todo_message',
                'message_type': message_type,
                'message': message
            }
        )

    # Receive message from room group
    async def todo_message(self, event):
        message_type = event['message_type']
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': message_type,
            'message': message
        }))

    @database_sync_to_async
    def get_user_todos(self, user):
        """Get todos for a specific user"""
        if isinstance(user, AnonymousUser):
            return []
        return list(Todo.objects.filter(user=user).values('id', 'title', 'status', 'priority'))

    @database_sync_to_async
    def create_todo(self, user, title, description='', priority='medium', status='pending'):
        """Create a new todo"""
        if isinstance(user, AnonymousUser):
            return None
        return Todo.objects.create(
            user=user,
            title=title,
            description=description,
            priority=priority,
            status=status
        )
