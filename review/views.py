from django.shortcuts import redirect, render
from django.contrib import messages


from review.models import ReviewsAndRating, RateGuest
from .forms import ReviewForm, GuestsReviewForm
from listings.models import Booking

def RatingAndReviewListings(request, listing_id):

    url     = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        booking         = Booking.objects.filter(room_id=listing_id, booking_progres='Completed', user_id=request.user.id)
        if booking:
            try:
                review      = ReviewsAndRating.objects.get(reviewer__id=request.user.id, room__id=listing_id)
                form        = ReviewForm(request.POST, instance=review)
                form.save()
                messages.success(request, "Thank you your review have been updated.")
                return redirect(url)
            except ReviewsAndRating.DoesNotExist:
                form        = ReviewForm(request.POST)
                if form.is_valid():
                    data                = ReviewsAndRating()
                    data.review         = form.cleaned_data['review']
                    data.rating         = form.cleaned_data['rating']
                    data.ip             = request.META.get('REMOTE_ADDR')
                    data.room_id        = listing_id
                    data.reviewer_id    = request.user.id
                    data.save()
                    messages.success(request, "Thank you your review have been submitted.")
                    return redirect(url)
        else:
            messages.info(request, "You must have book and completed booking to add a review.")
            return redirect(url)

def RatingAndReviewGuests(request, guest_id):

    url     = request.META.get('HTTP_REFERER')

    if request.method == 'POST':
        booking         = Booking.objects.filter(booking_progres='Completed', user_id=guest_id, room_host_id=request.user.id)
        if booking:
            try:
                review      = RateGuest.objects.get(guest__id=guest_id, host__id=request.user.id)
                form        = GuestsReviewForm(request.POST, instance=review)
                form.save()
                messages.success(request, "Thank you your review have been updated.")
                return redirect(url)
            except RateGuest.DoesNotExist:
                form        = GuestsReviewForm(request.POST)
                if form.is_valid():
                    data                = RateGuest()
                    data.review         = form.cleaned_data['review']
                    data.rating         = form.cleaned_data['rating']
                    data.ip             = request.META.get('REMOTE_ADDR')
                    data.guest_id       = guest_id
                    data.host_id        = request.user.id
                    data.save()
                    messages.success(request, "Thank you your review have been submitted.")
                    return redirect(url)
        else:
            messages.info(request, "Guests must have booked and completed booking to add a review.")
            return redirect(url)