from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

# SUPABASE
from django.http import JsonResponse
from utils.supabase_client import supabase

from .models import Room, Message


# Create your views here.
@login_required
def index(request):
    rooms = Room.objects.all()
    return render(request, "chat/index.html", {"rooms": rooms})


class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        response = supabase.auth.sign_up(
            {
                "email": email,
                "password": password,
            }
        )

        if "user" in response:
            return JsonResponse(
                {"success": True, "message": "User registered successfully"}
            )
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": response.get("error", "Registration failed"),
                }
            )
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"})


def login(request):

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        response = supabase.auth.sign_in(
            {
                "email": email,
                "password": password,
            }
        )

        if hasattr(response, "session"):
            return JsonResponse(
                {
                    "success": True,
                    "message": "User logged in successfully",
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                }
            )

        return JsonResponse({"success": False, "message": "Invalid credentials"})


def protected_view(request):
    if not request.user:
        return JsonResponse({"success": False, "message": "Authentication required"})

    return JsonResponse(
        {
            "success": True,
            "message": "Access granted to protected view",
            "user": request.user,
        }
    )


# SUPABASE REALTIME
from supabase import create_client, Client
import os

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_APIKEY")
supabase: Client = create_client(supabase_url, supabase_key)


def sendNotificationToUser(request):
    supabase.channel("sala1").send(
        {
            "type": "broadcast",
            "event": "notification",
            "payload": {
                "message": "Hello, world!",
            },
        }
    )
    return JsonResponse({"success": True, "message": "Notification sent successfully"})


def room(request, room_id):
    try:
        room = Room.objects.get(id=room_id)
        messages = Message.objects.filter(room=room)
    except Room.DoesNotExist:
        return render(request, "utils/404.html", {"message": "Oops! Room not found"})
    return render(request, "chat/room.html", {"room": room, "messages": messages})
