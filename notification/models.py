from mimetypes import guess_type
from django.db import models
from django.db.models.base import Model
from django.contrib.auth import get_user_model
from django.http import request

from listings.models import Listing

User = get_user_model()
# Create your models here.

class Notification(models.Model):

    notification_reciever   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notification_reciever")
    notification_message    = models.TextField(blank=False)
    room                    = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="The_room_booked", null=True)
    guest                   = models.ForeignKey(User, on_delete=models.CASCADE, related_name="The_one_who_is_booking_room", null=True)
    date                    = models.DateTimeField(auto_now_add=True)
    is_seen                 = models.BooleanField(default=False)

