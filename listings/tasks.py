from celery import shared_task
from .models import Booking
import datetime
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

@shared_task(bind=True)
def check_for_completed_booking(self):
    objects             = Booking.objects.filter(booking_progres='Booked')
    for object in objects:
        if object.check_out < datetime.date.today():
            object.booking_progres='Completed'
            object.save()
    return "Done"

@shared_task(bind=True)
def send_emails_host(self):
    users = get_user_model().objects.filter(host=True)
    for user in users:
        pass
    return "Done"

@shared_task(bind=True)
def send_emails_guest(self):
    users = get_user_model().objects.filter(guets=True)
    for user in users:
        pass
    return "Done"