from channels.generic.websocket import AsyncWebsocketConsumer
from redis.asyncio import Redis
from asgiref.sync import sync_to_async
import json
import logging
import os
from dotenv import load_dotenv

from .models import Message, Room

logger = logging.getLogger("chat")
load_dotenv()


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_name"]
        self.user = self.scope["user"]
        self.redis = Redis.from_url(os.getenv("REDIS_URL"))

        # Obtiene el nombre de la sala
        room_obj = await get_room(self.room_id)
        self.room_name = room_obj.name  # nombre visible

        if room_obj:
            # El grupo usa el ID, no el nombre
            self.room_group_name = f"room_{self.room_id}"

            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()

            # Notifica al usuario
            await self.send(
                json.dumps(
                    {
                        "type": "notification",
                        "message": f"Bienvenido {self.user.username} a la sala {self.room_name}",
                        "user": "system",
                    }
                )
            )

            # Añadir usuario actual a Redis
            await self.redis.sadd(self.room_group_name, self.user.username)

            # Notificar a todos los usuarios con nueva lista
            users = await self.redis.smembers(self.room_group_name)
            users = [u.decode() for u in users]  # <–– DECODIFICAR

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "list_users",
                    "users": users,
                },
            )

        else:
            await self.close()

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        # guardar mensaje en DB
        await save_message(self.room_id, message, self.user)

        # enviar a grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": self.user.username,
            },
        )

    async def chat_message(self, event):
        await self.send(
            json.dumps(
                {
                    "type": "chat_message",
                    "message": event["message"],
                    "user": event["user"],
                }
            )
        )

    async def list_users(self, event):
        await self.send(
            json.dumps(
                {
                    "type": "list_users",
                    "users": event["users"],
                }
            )
        )

    async def notification(self, event):
        await self.send(
            json.dumps(
                {
                    "type": "notification",
                    "message": event["message"],
                }
            )
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Quitar usuario del set
        await self.redis.srem(self.room_group_name, self.user.username)

        # Lista actualizada
        users = await self.redis.smembers(self.room_group_name)
        users = [u.decode() for u in users]

        # Notificar salida
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "list_users",
                "users": users,
            },
        )


@sync_to_async
def get_room(room_id):
    return Room.objects.get(id=room_id)


@sync_to_async
def save_message(room_id, message, user):
    room = Room.objects.get(id=room_id)
    Message.objects.create(room=room, user=user, content=message)
