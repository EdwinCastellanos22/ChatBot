from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from redis.asyncio import Redis
import datetime
import json


# CHAT GENERAL
class ChatConsumer(AsyncWebsocketConsumer):

    # --- Connect ---
    async def connect(self):
        self.username = self.path_params = self.scope["url_route"]["kwargs"].get(
            "username"
        )
        self.room_name = "General"

        # connect to redis
        self.redis = Redis(host="127.0.0.1", port=6379, decode_responses=True)

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        # add user to redis
        await self.redis.sadd(self.room_name, self.username)

        # -- send list of users in room ---
        users = await self.redis.smembers(self.room_name)
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "send_users_list",
                "users": list(users),
            }
        )

        # send last 50 messages
        last_messages = await self.get_messages()
        for msg in last_messages:
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "chat_message",
                    "message": msg["content"],
                    "username": msg["username"],
                    "timestamp": msg["timestamp"],
                },
            )

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "notification",
                "message": f"🔔 {self.username} se ha unido al chat!.",
                "username": "System",
                "timestamp": datetime.datetime.utcnow()
                .replace(microsecond=0)
                .isoformat()
                + "Z",
            },
        )
        print(f"User connected to ws: {self.username}")

    # --- Desconnect ---
    async def disconnect(self, code):
        await self.redis.srem(self.room_name, self.username)

        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "notification",
                "message": f"🔔 {self.username} a salido del chat!.",
                "username": "System",
                "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )

        await self.channel_layer.group_discard(self.room_name, self.channel_name)

        if self.redis:
            await self.redis.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data)
        message = data["message"]
        username = self.username

        # send to users in group
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
                "timestamp": datetime.datetime.utcnow()
                .replace(microsecond=0)
                .isoformat()
                + "Z",
            },
        )

        # save to DB
        await self.save_message(self.username, message)

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "message": event["message"],
                    "username": event["username"],
                    "timestamp": datetime.datetime.utcnow()
                    .replace(microsecond=0)
                    .isoformat()
                    + "Z",
                }
            )
        )

    async def notification(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notification",
                    "message": event["message"],
                    "username": event["username"],
                    "timestamp": event.get(
                        "timestamp",
                        datetime.datetime.utcnow().replace(microsecond=0).isoformat()
                        + "Z",
                    )
                    + "Z",
                }
            )
        )
        
    async def send_users_list(self, event):
        await self.send(text_data=json.dumps({
            "type": "users_list",
            "users": event["users"]
        }))


    @database_sync_to_async
    def save_message(self, user, content):
        try:
            room, _ = Room.objects.get_or_create(name="General")
            Message.objects.create(user=user, room=room, content=content)
        except Exception as e:
            print("Error saving message:", e)
            pass

    @database_sync_to_async
    def get_messages(self):
        try:
            room, _ = Room.objects.get_or_create(name="General")
            messages = Message.objects.filter(room=room).order_by("-timestamp")[:50]
            return [
                {
                    "username": msg.user.username,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() + "Z",
                }
                for msg in messages
            ][::-1]
        except Exception as e:
            print("Error fetching messages:", e)
            return []


# CHAT POR SALA
class RoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]
        self.username = self.user.username if self.user.is_authenticated else "Anon"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": f"🔔 {self.username} se ha unido a la sala!",
                "username": "System",
                "timestamp": str(datetime.datetime.utcnow().isoformat()) + "Z",
            },
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        user = self.scope["user"]

        username = user.username if user.is_authenticated else "Anon"

        # save to DB
        await self.save_message(
            self.room_name, user if user.is_authenticated else None, message
        )

        # send message to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
                "timestamp": str(datetime.datetime.utcnow().isoformat()) + "Z",
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "username": event["username"],
                    "timestamp": event.get(
                        "datetime", str(datetime.datetime.utcnow().isoformat())
                    )
                    + "Z",
                }
            )
        )

    @database_sync_to_async
    def save_message(self, roomName, user, content):
        room, _ = Room.objects.get_or_create(name=roomName)
        Message.objects.create(user=user, room=room, content=content)
