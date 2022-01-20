from django.db.models.signals import post_save 
from django.dispatch import receiver

from notification.models import Notification
from .models import RateGuest, ReviewsAndRating

@receiver(post_save, sender=ReviewsAndRating)
def get_notofication_rating_room(sender, created, instance, *args, **kwargs):
    room_rated       = instance
    notifi_reciever = room_rated.room.user
    room_id         = room_rated.room
    guest           = room_rated.reviewer.full_name
    noti_message    = f"""{guest} rated your {room_rated.room.title}, {room_rated.room.exact_address}
                        with {room_rated.rating} stars and commented ''{room_rated.review}''.
                    """
    notification        = Notification.objects.create(
        notification_reciever       =   notifi_reciever,
        notification_message        =   noti_message,
        room                        =   room_id,
        guest                       =   room_rated.reviewer,
        )
    notification.save()

@receiver(post_save, sender=RateGuest)
def get_notofication_rating_guests(sender, created, instance, *args, **kwargs):
    room_rated      = instance
    notifi_reciever = room_rated.guest
    guest           = room_rated.host
    noti_message    = f"""{guest.full_name} rated you with {room_rated.rating} stars and 
                    commented ''{room_rated.review}'' after you completed his booking.
                    """
    notification        = Notification.objects.create(
        notification_reciever       =   notifi_reciever,
        notification_message        =   noti_message,
        guest                       =   guest,
        )
    notification.save()