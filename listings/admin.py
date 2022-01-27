from django.contrib import admin
from .models import Booking, Refund_Control, RoomLocation, Listing, Contact

admin.site.register(RoomLocation)

class LisitngAdmin(admin.ModelAdmin):

    list_display    = ['title','city','exact_address', 'approved', 'is_published']
    list_filter     = ['approved', 'is_published', 'listing_type', 'kitchen_available']
    search_fields   = ['title']

admin.site.register(Listing, LisitngAdmin)

class BookingAdmin(admin.ModelAdmin):
    list_display    = ['uuid','date_booked','user_full_name', 'room_host_full_name', 'check_in', 'check_out', 'total_amount']
    search_fields   = ['user_email', 'user_full_name', 'room_host_email', 'room_host_phone', 'room_host_full_name', 'check_in', 'check_out']

admin.site.register(Booking, BookingAdmin)

admin.site.register(Contact)

class RefundControlAdmin(admin.ModelAdmin):
    list_display    = ['booking_staus','total_amount','refund_percentage', 'refund_completed',]
    search_fields   = ['booking_staus','total_amount','refund_percentage',]

admin.site.register(Refund_Control, RefundControlAdmin)
# Register your models here.
