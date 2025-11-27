from django.urls import re_path
from chat import consumer, consumer_rooms
from . import views


websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<username>\w+)/$", consumer.ChatConsumer.as_asgi()),
    re_path(r"ws/room/(?P<room_name>\w+)/$", consumer_rooms.RoomConsumer.as_asgi()),
]
