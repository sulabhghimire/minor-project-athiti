import datetime
from listings.models import Listing, Booking

def check_availability(room, check_in, check_out):
    avail_list  = []
    Booking_list    = Booking.objects.filter(room_id=room, booking_progres='Booked' )
    for booking in Booking_list:
        if booking.check_in >= check_out or booking.check_out<= check_in:
            avail_list.append(True)
        else:
            avail_list.append(False)
    return all(avail_list)