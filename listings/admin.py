from django.contrib import admin
from .models import Booking, Refund_Control, RoomLocation, Listing, Contact

admin.site.register(RoomLocation)
admin.site.register(Listing)
admin.site.register(Booking)
admin.site.register(Contact)
admin.site.register(Refund_Control)
# Register your models here.
