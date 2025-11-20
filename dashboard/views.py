from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from chat.models import Room, Message
import datetime
import socket
import json


@login_required
def dashboard_view(request):
    # Datos existentes
    user_count = User.objects.count()
    room_count = Room.objects.count()
    message_count = Message.objects.count()

    # Nuevos datos para el dashboard
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_user = request.user
    hostname = socket.gethostname()

    # Datos para el gráfico
    chart_data = {
        "labels": ["Usuarios", "Salas", "Mensajes"],
        "data": [user_count, room_count, message_count],
    }

    context = {
        "user_count": user_count,
        "room_count": room_count,
        "message_count": message_count,
        "current_time": current_time,
        "current_user": current_user,
        "hostname": hostname,
        "chart_data": json.dumps(chart_data),
    }
    return render(request, "dashboard/index.html", context)
