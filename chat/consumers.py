import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        print("[CONNECT] User:", self.user)

        if not self.user or not self.user.is_authenticated:
            await self.close()
            return

        try:
            self.other_user_id = int(self.scope["url_route"]["kwargs"]["user_id"])
        except (KeyError, ValueError):
            print("[ERROR] Invalid or missing user_id in URL")
            await self.close()
            return

        self.room_group_name = self.get_room_group_name(self.user.id, self.other_user_id)
        print("[ROOM JOIN] Room Group:", self.room_group_name)

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        print(f"[DISCONNECT] User {self.user} from room {self.room_group_name}")
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message", "").strip()
            if not message:
                print("[WARN] Empty message ignored")
                return

            saved_msg = await self.save_message(
                sender_id=self.user.id,
                receiver_id=self.other_user_id,
                content=message
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": saved_msg["content"],
                    "sender": saved_msg["sender"],
                    "timestamp": saved_msg["timestamp"],
                }
            )

            print(f"[RECEIVE] Message sent in room {self.room_group_name}")
        except Exception as e:
            print("[ERROR] receive:", e)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"],
            "timestamp": event["timestamp"],
        }))
        print(f"[SEND] Delivered message to user {self.user.id}")

    def get_room_group_name(self, user1_id, user2_id):
        ids = sorted([user1_id, user2_id])
        return f"chat_room_{ids[0]}_{ids[1]}"

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, content):
        users = sorted([sender_id, receiver_id])

        # Get or create the room with both participants
        room = ChatRoom.objects.filter(participants__id=users[0]) \
                               .filter(participants__id=users[1]) \
                               .distinct().first()
        if not room:
            room = ChatRoom.objects.create()
            room.participants.add(*users)

        msg = ChatMessage.objects.create(
            room=room,
            sender_id=sender_id,
            content=content
        )

        return {
            "content": msg.content,
            "sender": msg.sender.id,
            "timestamp": str(msg.timestamp),
        }
