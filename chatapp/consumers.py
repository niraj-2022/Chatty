import json
from blinker import receiver_connected
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatMsg


User = get_user_model()


class ChatappConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        user = self.scope['user']
        print('*******[CONNECTED]*******', user)
        chatroom = f'user_chatroom_{user.username}'
        self.chatroom = chatroom

        await self.channel_layer.group_add(
            chatroom,
            self.channel_name
        )

        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        received_msg = json.loads(event['text'])
        message = received_msg.get('message')
        sender = received_msg.get('sender')
        receiver = received_msg.get('receiver')

        print(f"*******[MESSAGE RCVD]*******\n\
            SENDER: {sender}; RECEIVER: {receiver}; MESSAGE: {message}")

        if not message:
            print("*******[ERROR] Empty Message")
            return False

        senderObject = await self.get_user_object(sender)
        receiverObject = await self.get_user_object(receiver)

        if not senderObject:
            print("*******[ERROR] Sender Error")
        if not receiverObject:
            print("*******[ERROR] Receiver Error")

        receiver_chatroom = f'user_chatroom_{receiver}'
        self_user = self.scope['user']
        response = {
            'message': message,
            'sender': self_user.username,
            'receiver': receiver
        }

        await self.store_message(response)

        await self.channel_layer.group_send(
            receiver_chatroom,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

        await self.channel_layer.group_send(
            self.chatroom,
            {
                'type': 'chat_message',
                'text': json.dumps(response)
            }
        )

    async def websocket_disconnect(self, event):
        print('*******[DISCONNECTED]*******', event)

    @database_sync_to_async
    def store_message(self, obj):
        queryset = ChatMsg.objects.create(
            sender=obj['sender'], receiver=obj['receiver'], message=obj['message'])
        queryset.save()

    async def chat_message(self, event):
        obj = json.loads(event['text'])

        await self.send({
            'type': 'websocket.send',
            'text': event['text']
        })

    @database_sync_to_async
    def get_user_object(self, username):
        queryset = User.objects.filter(username=username)

        obj = None
        if queryset.exists():
            obj = queryset.first()

        return obj
