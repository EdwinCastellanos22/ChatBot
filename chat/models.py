from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Room(models.Model):
    name= models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    
    
class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default= timezone.now)
    
    class Meta:
        ordering = ['timestamp']
        
    def __str__(self):
        return f"[{self.room}] || [{self.user}] || [{self.content[:20]}]"