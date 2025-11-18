from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

#SUPABASE
from django.http import JsonResponse
from utils.supabase_client import supabase

from .models import Room, Message

# Create your views here.
@login_required
def index(request):
    
    return render(request, "chat/index.html", )


class RegisterView(generic.CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("login")


def register(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        
        if 'user' in response:
            return JsonResponse({"success": True, "message": "User registered successfully"})
        else:
            return JsonResponse({"success": False, "message": response.get('error', 'Registration failed')})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"})
    
    
def login(request):
    
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        response = supabase.auth.sign_in({
            "email": email,
            "password": password,
        })
        
        if hasattr(response, 'session'):
            return JsonResponse({"success": True, "message": "User logged in successfully",
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            })
            
        return JsonResponse({"success": False, "message": "Invalid credentials"})
    

def protected_view(request):
    if not request.user:
        return JsonResponse({"success": False, "message": "Authentication required"})
    
    return JsonResponse({
        "success": True, 
        "message": "Access granted to protected view",
        "user": request.user
    })