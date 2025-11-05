from django.urls import re_path
from chat import consumer

websocket_urlpatterns = [
    # Pasando username por URL
    re_path(r"ws/chat/(?P<username>\w+)/$", consumer.ChatConsumer.as_asgi()),

    # Salas dinámicas normales
    re_path(r"ws/chat/room/(?P<room_name>\w+)/$", consumer.RoomConsumer.as_asgi()),
]
