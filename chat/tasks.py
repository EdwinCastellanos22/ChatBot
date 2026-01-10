from celery import shared_task
from .ia_moderation import message_moderate
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


logger = logging.getLogger("chat")

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 3},
)
def analize_message(self, message, group_name, username):
    offensive = message_moderate(message)
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "moderation",
            "result": offensive,
            "message": message,
            "username": username,
        }
    )