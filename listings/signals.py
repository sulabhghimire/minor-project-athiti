from notification.models import Notification
from .models import Booking, Listing, Refund_Control
from django.db.models.signals import post_save 
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=Booking)
def create_notification(sender, instance, *args, **kwargs):
    booking         = instance
    not_reciever    = User.objects.get(id=booking.user_id)
    room            = Listing.objects.get(id=booking.room_id)
    checkin         = str(booking.check_in)
    checkout        = str(booking.check_out)
    if booking.booking_progres=="Booked":
        not_message     = f"""You have booked {room.listing_type} located at {room.city},
                          {room.exact_address} from {checkin} to {checkout}. 
                          You have paid {booking.total_amount} for the service. Please be 
                          on time and enjoy your stay. Have no hesitation to contact us in
                          case of any problem.
        """
    elif booking.booking_progres=="Cancelled":
        not_message     = f"""You have cancelled booking {room.listing_type} located at {room.city},
                          {room.exact_address}.If you are eledigble or refund then it shall take 8 
                          wokring days to be done.Have no hesitation to contact us in
                          case of any problem.
        """
    elif booking.booking_progres=="Completed":
        not_message     = f"""Your {room.listing_type} booking located at {room.city},
                          {room.exact_address} that from {checkin} to {checkout} 
                          was sucessfuly completed. You can rate the room if you want.
        """
    notify          = Notification(notification_reciever=not_reciever, notification_message=not_message, room=room, guest=not_reciever)
    notify.save()

@receiver(post_save, sender=Booking)
def create_notification_for_host(sender, instance, *args, **kwargs):
    booking         = instance
    not_reciever    = User.objects.get(id=booking.room_host_id)
    guest           = User.objects.get(id=booking.user_id)
    room            = Listing.objects.get(id=booking.room_id)
    checkin         = str(booking.check_in)
    checkout        = str(booking.check_out)
    if booking.booking_progres=="Booked":
        not_message     = f"""Your {room.listing_type} located at {room.city},
                          {room.exact_address} has been booked from {checkin} to {checkout}.
        """
    elif booking.booking_progres=="Cancelled":
        not_message     = f"""Your {room.listing_type} located at {room.city},
                          {room.exact_address} that had been booked from {checkin} to {checkout} 
                          was cancelled.
        """
    elif booking.booking_progres=="Completed":
        not_message     = f"""Your {room.listing_type} located at {room.city},
                          {room.exact_address} that had been booked from {checkin} to {checkout} 
                          was sucessfuly completed. You will recieve full payment in 2 working
                          days. You can rate the guest if you want.
        """
    notify          = Notification(notification_reciever=not_reciever, notification_message=not_message,  room=room, guest=guest)
    notify.save()

@receiver(post_save, sender=Refund_Control)
def create_refund_status_notification(sender, instance, *args, **kwargs):
    refund         = instance
    not_reciever   = User(id = refund.booking_staus.user_id)
    if refund.refund_percentage=='0':
        not_message = f"""
                    Since you cancelled your booking upto 2 days before your check in date so
                    you are not eldgible for any of the refund. Please feel free to contact us in
                    case of any dis-satisfication. Thank you.
        """
    elif refund.refund_percentage=='50':
        not_message = f"""
                   Since you cancelled your booking before 3 days your check in date so
                    you are eldgible for half refund. Please feel free to contact us in
                    case of any dis-satisfication. Thank you.
        """
    elif refund.refund_percentage=='100':
        not_message = f"""
                    Since you cancelled your booking 7 days before your check in date so
                    you are eldgible for full refund. Please feel free to contact us in
                    case of any dis-satisfication. Thank you.
        """

    notify          = Notification(notification_reciever=not_reciever, notification_message=not_message)
    notify.save()

