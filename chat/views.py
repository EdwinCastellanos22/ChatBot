from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

from .models import Room, Message

# Create your views here.
@login_required
def index(request):
    
    rooms = Room.objects.all()
    general = Room.objects.get(id=5)
    messages = Message.objects.filter(room= general)
    return render(request, "chat/index.html", { "rooms": rooms, "messages": messages})


class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


