from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message
from redis.asyncio import Redis
import datetime
import json

import logging
logger = logging.getLogger('chat')


# CHAT GENERAL
class ChatConsumer(AsyncWebsocketConsumer):

    # --- Connect ---
    async def connect(self):
        self.username = self.path_params = self.scope["url_route"]["kwargs"].get(
            "username"
        )
        self.room_name = "General"
        
        logger.info(f"User connected to ws: {self.username} : {self.room_name}")


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

        # # send last 50 messages
        # last_messages = await self.get_messages()
        # for msg in last_messages:
        #     await self.channel_layer.group_send(
        #         self.room_name,
        #         {
        #             "type": "chat_message",
        #             "message": msg["content"],
        #             "username": msg["username"],
        #             "timestamp": msg["timestamp"],
        #         },
        #     )

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
        logger.info(f"User disconnected from ws: {self.username} : {self.room_name}")

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
        message = data["message"]
        username = self.username
        
        logger.info(f"Message received from {username}({self.room_name}): {message}")

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

        # # save to DB
        # await self.save_message(self.username, message)

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
