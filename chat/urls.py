from django.contrib import admin
from django.urls import path
from .views import index, room

urlpatterns = [
    path("general/", index, name="Chat"),
    path("room/<int:room_id>/", room, name="Room"),
]
