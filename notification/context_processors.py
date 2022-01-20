from django.conf import settings
from notification.models import Notification
import datetime

def admin_media(request):
    count_notifications     = None
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(is_seen=True, notification_reciever=request.user)
        if notifications:
            for notifi in notifications:
                past      = notifi.date.strftime("%Y-%m-%d")
                total_days = int((datetime.date.today() - datetime.datetime.strptime(past, '%Y-%m-%d').date()).days)
                if total_days >= 2:
                    Notification.objects.get(id=notifi.id).delete()
        count_notifications = Notification.objects.filter(notification_reciever=request.user, is_seen=False).count()
    return {'count_notifications': count_notifications}