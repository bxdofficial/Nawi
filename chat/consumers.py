"""
WebSocket consumers for real-time chat and notifications
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """Consumer for chat messages"""
    
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.conversation_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope["user"]
        
        # Join conversation group
        await self.channel_layer.group_add(
            self.conversation_group_name,
            self.channel_name
        )
        
        # Update user online status
        await self.set_user_online(True)
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'message': 'Connected to chat'
        }))
    
    async def disconnect(self, close_code):
        # Leave conversation group
        await self.channel_layer.group_discard(
            self.conversation_group_name,
            self.channel_name
        )
        
        # Update user online status
        await self.set_user_online(False)
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'message':
            await self.handle_message(text_data_json)
        elif message_type == 'typing':
            await self.handle_typing(text_data_json)
        elif message_type == 'read':
            await self.handle_read_receipt(text_data_json)
    
    async def handle_message(self, data):
        """Handle chat message"""
        message = data['message']
        
        # Save message to database
        saved_message = await self.save_message(message)
        
        # Send message to conversation group
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user_id': str(self.user.id),
                'user_name': self.user.name,
                'message_id': str(saved_message.id),
                'timestamp': saved_message.sent_at.isoformat()
            }
        )
    
    async def handle_typing(self, data):
        """Handle typing indicator"""
        is_typing = data.get('is_typing', False)
        
        await self.channel_layer.group_send(
            self.conversation_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'user_name': self.user.name,
                'is_typing': is_typing
            }
        )
    
    async def handle_read_receipt(self, data):
        """Handle read receipt"""
        message_id = data.get('message_id')
        
        if message_id:
            await self.mark_message_as_read(message_id)
            
            await self.channel_layer.group_send(
                self.conversation_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'user_id': str(self.user.id)
                }
            )
    
    # Receive message handlers
    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp']
        }))
    
    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'is_typing': event['is_typing']
        }))
    
    async def read_receipt(self, event):
        """Send read receipt to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'read',
            'message_id': event['message_id'],
            'user_id': event['user_id']
        }))
    
    # Database operations
    @database_sync_to_async
    def save_message(self, message_content):
        from chat.models import Message, Conversation
        
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=self.user,
            content=message_content,
            message_type='text'
        )
        return message
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        from chat.models import Message
        
        try:
            message = Message.objects.get(id=message_id)
            message.mark_as_read()
        except Message.DoesNotExist:
            pass
    
    @database_sync_to_async
    def set_user_online(self, is_online):
        from chat.models import OnlineStatus
        
        status, created = OnlineStatus.objects.get_or_create(user=self.user)
        if is_online:
            status.set_online(self.channel_name)
        else:
            status.set_offline()


class NotificationConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time notifications"""
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.user_group_name = f'user_{self.user.id}'
        
        # Join user notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send unread notifications count
        unread_count = await self.get_unread_notifications_count()
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'unread_count': unread_count
        }))
    
    async def disconnect(self, close_code):
        # Leave user notification group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        text_data_json = json.loads(text_data)
        action = text_data_json.get('action')
        
        if action == 'mark_read':
            notification_id = text_data_json.get('notification_id')
            if notification_id:
                await self.mark_notification_as_read(notification_id)
        elif action == 'get_all':
            notifications = await self.get_all_notifications()
            await self.send(text_data=json.dumps({
                'type': 'all_notifications',
                'notifications': notifications
            }))
    
    async def notification(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    async def update_count(self, event):
        """Update unread notifications count"""
        await self.send(text_data=json.dumps({
            'type': 'update_count',
            'unread_count': event['unread_count']
        }))
    
    # Database operations
    @database_sync_to_async
    def get_unread_notifications_count(self):
        from chat.models import Notification
        return Notification.objects.filter(
            user=self.user,
            is_read=False
        ).count()
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        from chat.models import Notification
        
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def get_all_notifications(self):
        from chat.models import Notification
        
        notifications = Notification.objects.filter(
            user=self.user
        ).order_by('-created_at')[:20]
        
        return [{
            'id': str(n.id),
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat(),
            'action_url': n.action_url,
            'action_text': n.action_text
        } for n in notifications]