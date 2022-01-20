from django.urls import path
from . import views


urlpatterns = [
    path('', views.ShowNotificationsGuests, name='notifications'),
    path('delete_noti/<int:pk>', views.DeleteNotiGuests, name='delete-noti')
]