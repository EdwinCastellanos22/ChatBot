from django.contrib import admin
from django.urls import path
from .views import index

urlpatterns = [
    path("general/", index, name="Chat")
]