from channels.generic.websocket import AsyncWebsocketConsumer
from redis.asyncio import Redis
import datetime
import json
import logging
import os
from dotenv import load_dotenv
import html

#celery
from .tasks import analize_message

logger = logging.getLogger("chat")
load_dotenv()


def utc_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.username = self.scope["url_route"]["kwargs"].get("username")
        self.room_name = "General"

        logger.info(f"User connected to ws: {self.username} : {self.room_name}")

        # connect to redis
        try:
            self.redis = Redis.from_url(os.getenv("REDIS_URL"))
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            await self.close()
            return

        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        # Add user to redis set
        await self.redis.sadd(self.room_name, self.username)

        # Send updated users list
        users = {u.decode() for u in await self.redis.smembers(self.room_name)}
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "send_users_list",
                "users": list(users),
            },
        )

        # Broadcast user online
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "status_online",
                "username": self.username,
                "status": "online",
            },
        )

        # System join notification
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "notification",
                "message": f"{self.username} se ha unido al chat!",
                "username": "System",
                "timestamp": utc_now(),
            },
        )

    async def disconnect(self, code):
        await self.redis.srem(self.room_name, self.username)

        # Broadcast offline
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "status_offline",
                "username": self.username,
                "status": "offline",
            },
        )

        logger.info(f"User disconnected: {self.username}")

        # System notification
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "notification",
                "message": f"{self.username} ha salido del chat!",
                "username": "System",
                "timestamp": utc_now(),
            },
        )

        await self.channel_layer.group_discard(self.room_name, self.channel_name)

        if self.redis:
            await self.redis.close()
            
    
    async def receive(self, text_data):
        data = json.loads(text_data)

        # typing indicator
        if data.get("typing"):
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "typing",
                    "username": self.username,
                },
            )
            return

        # stop typing indicator
        if data.get("stop_typing"):
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "stop_typing",
                    "username": self.username,
                },
            )
            return

        # Normal message
        message = html.escape(data.get("message"))
        analize_message.delay(message=message,  group_name=self.room_name, username=self.username)

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "message",
                    "message": event["message"],
                    "username": event["username"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def notification(self, event):
        await self.send(json.dumps(event))

    async def send_users_list(self, event):
        await self.send(json.dumps({"type": "users_list", "users": event["users"]}))

    async def typing(self, event):
        await self.send(json.dumps({"type": "typing", "username": event["username"]}))

    async def stop_typing(self, event):
        await self.send(
            json.dumps({"type": "stop_typing", "username": event["username"]})
        )

    async def status_online(self, event):
        await self.send(json.dumps(event))

    async def status_offline(self, event):
        await self.send(json.dumps(event))
        
    async def moderation(self, event):
        if event['result'] :
            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "notification",
                    "message": f"Mensaje de {event['username']} bloqueado por contenido ofensivo.",
                    "username": "System",
                    "timestamp": utc_now(),
                },
            )
            
        else:
            message = html.escape(event["message"])
            logger.info(f"Message from {self.username}: {message}")

            await self.channel_layer.group_send(
                self.room_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": self.username,
                    "timestamp": utc_now(),
                },
            )