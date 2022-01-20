from django.shortcuts import redirect, render
from .models import Notification, User

def ShowNotificationsGuests(request):
    user            = request.user
    notifications   = Notification.objects.filter(notification_reciever=user).order_by('-date')
    Notification.objects.filter(notification_reciever=user, is_seen=False).update(is_seen=True)

    context = {
        'notifs' : notifications,
    }
    return render(request, 'notification/notifications.html', context)

def DeleteNotiGuests(request, pk):
    
    url     = request.META.get('HTTP_REFERER')

    user            = request.user
    Notification.objects.get(notification_reciever=user, id=pk).delete()

    return redirect(url)