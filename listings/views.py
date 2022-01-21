from turtle import color
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.template import context
from django.urls import reverse
from django.http.response import Http404, HttpResponse, HttpResponseRedirect
from .forms import AvailabilityForm, ContactUsForm
import datetime
from decimal import Decimal

from . models import Listing, Booking, Refund_Control
import review.models as rev_model

from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic import DetailView, UpdateView, CreateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, AccessMixin
from django.core.paginator import Paginator
from listings.booking_functions.availability import check_availability

# Create your views here.

def CancelBooking(request, pk):
    obj                       = Booking.objects.get(id=pk)
    check_in_date             = obj.check_in
    current_date              = datetime.date.today()
    rem_days                  = int((check_in_date-current_date).days )
    if rem_days <=2 :
        obj.refund_status        = 'You aren\'t eledgible for any refund'
        refund_percentage = '0'
    elif rem_days<=7:
        obj.refund_status        = 'Cancelled - You are eledgible for 50% refund of your booking amount'
        refund_percentage = '50'
    else:
        obj.refund_status           = 'Cancelled - You are eledgible for 100% refund of your booking amount'
        refund_percentage = '100'
    obj.booking_progres       = 'Cancelled' 
    refund                    = Refund_Control.objects.create(
       booking_staus          = obj,
       sum_amount             = obj.sum_amount,
       tax_amount             = obj.tax_amount,
       service_charge_amount  = obj.service_charge_amount,
       total_amount           = obj.total_amount,
       refund_percentage      = refund_percentage,
    )
    obj.save()
    return redirect('guests-booking')
    

class GuestsListingView(LoginRequiredMixin, ListView, AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.host == True:
            raise Http404
        return super().dispatch(request, *args, **kwargs)
    
    objects             = Booking.objects.filter(booking_progres='Booked')
    for object in objects:
        if object.check_out < datetime.date.today():
            object.booking_progres='Completed'
            object.save()
    model               = Booking
    template_name       = 'listings/guest_booking_info.html'
    context_object_name = 'posts'

class HostsListingView(LoginRequiredMixin, ListView, AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.guest == True:
            raise Http404
        return super().dispatch(request, *args, **kwargs)
    
    objects             = Booking.objects.filter(booking_progres='Booked')
    for object in objects:
        if object.check_out < datetime.date.today():
            object.booking_progres='Completed'
            object.save()
    model               = Booking
    template_name       = 'listings/host_bookings_info.html'
    context_object_name = 'posts'
    
def home(request):
    return render(request, 'listings/home.html')

class ListListings(LoginRequiredMixin, ListView, AccessMixin):
    
    template_name = 'listings/all_listings.html'

    model   = Listing
    context_object_name = 'posts'

def CheckRoomAvabiality(request):

    url     = request.META.get('HTTP_REFERER')
    
    if request.method == 'POST':
        form            = AvailabilityForm(request.POST)
        if form.is_valid():
            data    = form.cleaned_data
            rooms   = Listing.objects.filter(id=data['room_name'])
            available_rooms = []

            if data['check_in'] < datetime.date.today():
                messages.info(request, f'You can\'t checkin in past.')
            elif data['check_out'] < datetime.date.today():
                messages.info(request, f'You can\'t checkout in past.')
            elif data['check_out'] < data['check_in']:
                messages.info(request, f'Check Out Date can\'t be earlier than Check In date.')    
            else:
                for room in rooms:
                    if check_availability(room.id, data['check_in'], data['check_out']):
                        available_rooms.append(room)
                
                if len(available_rooms)>0:
                    messages.success(request, f'Room is available.')
                else:
                    messages.success(request, f'Room is not available.')

        return redirect(url)

import folium
def LisitngDetailView(request, pk):

    obj     = Listing.objects.get(id=pk, is_published=True, approved=True)
    reviews = rev_model.ReviewsAndRating.objects.filter(room_id=pk, status=True)
    
    map     = folium.Map(location=[28.3974, 84], tiles="OpenStreetMap", zoom_start=7)
    lat, lng = float(obj.lat), float(obj.lng)
    folium.Marker(location=[lat, lng], popup=obj.title, tooltip="Click for More").add_to(map)
    map     = map._repr_html_()

    if reviews: 
        star    = 0
        count   = 0
        for review in reviews:
            star    = star + review.rating
            count   = count + 1

        stars = find_stars(star/count)

        if obj.rating != stars:
            obj.rating =  stars
            obj.save()

        if obj.total_bookings != count:
            obj.total_bookings = count
            obj.save()

    context = {
        'object'  : obj,
        'reviews' : reviews,
        'map'     : map, 
    }
    if obj:
        return render(request, 'listings/listing_details.html', context)
    else:
        raise Http404

def check_host(user):
    if user.is_authenticated:
        if user.host:
            return True
    else:
        return False

from .forms import PostForm
def post_item(request):

    if request.user.host:
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                Listing.objects.create(
                    user                = request.user,
                    title               = data['title'],
                    city                = data['city'],
                    exact_address       = data['exact_address'],
                    lat                 = data['lat'],
                    lng                 = data['lng'],
                    description         = data['description'],
                    price               = data['price'],
                    listing_type        = data['listing_type'],
                    kitchen_available   = data['kitchen_available'],
                    kitchen_description = data['kitchen_description'],
                    bedrooms            = data['bedrooms'],
                    max_acomodation     = data['max_acomodation'],
                    bathroom_type       = data['bathroom_type'],
                    no_bathrooms        = data['no_bathrooms'],
                    room_type           = data['room_type'],
                    main_photo          = data['main_photo'],
                    photo_1             = data['photo_1'],
                    photo_2             = data['photo_2'],
                    photo_3             = data['photo_3'],
                    is_published        = data['is_published'],
                )
                messages.success(request, "Your listing has been saved You will be able to view after it has been approved by admin!")
                return redirect('listing-list')
            else:
                messages.warning(request, "Your form is invalid!")
                return redirect('listing-post')

        form    = PostForm()
        context = {
            'form'  : form,
        }

        return render(request, "listings/post_listing.html", context)
    else:
        raise Http404

@user_passes_test(check_host)
def update_item(request, pk):

    listing = get_object_or_404(Listing, id=pk)

    if request.user== listing.user:

        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data

                Listing.objects.filter(id=pk).update(
                    title               = data['title'],
                    city                = data['city'],
                    exact_address       = data['exact_address'],
                    lat                 = data['lat'],
                    lng                 = data['lng'],
                    description         = data['description'],
                    price               = data['price'],
                    listing_type        = data['listing_type'],
                    kitchen_available   = data['kitchen_available'],
                    kitchen_description = data['kitchen_description'],
                    bedrooms            = data['bedrooms'],
                    max_acomodation     = data['max_acomodation'],
                    bathroom_type       = data['bathroom_type'],
                    no_bathrooms        = data['no_bathrooms'],
                    room_type           = data['room_type'],
                    main_photo          = data['main_photo'],
                    photo_1             = data['photo_1'],
                    photo_2             = data['photo_2'],
                    photo_3             = data['photo_3'],
                    is_published        = data['is_published'],
                )
                messages.success(request, "Your listing has been updated!")
                return redirect('listing-list')
            else:
                messages.warning(request, "Your form is invalid!")
                return redirect('listing-update', kwargs={'pk': pk})

        form    = PostForm(instance=listing)
        context = {
            'form'  : form,
            'lng'   : listing.lng,
            'lat'   : listing.lat,
        }

        return render(request, "listings/listing_update.html", context)

    else:
        raise Http404

class ListingDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Listing
    template_name   = 'listings/listing_confirm_delete.html'

    def get_success_url(self):
        messages.success(self.request, f'Your lisitng has been deleted.')
        return reverse('listing-list')

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.user:
            messages.success(self.request, f'Your lisitng has been updated.')
            return True
        return False

def SearchTitle(request):

    def SendRatingNumerical(word):
        if word=="--------":
            return 6
        elif word=="5":
            return 5
        elif word=="4+":
            return 4
        elif word=="3+":
            return 3
        elif word=="2+":
            return 2
        elif word=="1+":
            return 1
        elif word=="0+":
            return 0
        else:
            return 6
            

    if request.method == "POST":  
        
        ratings_by  = request.POST['ratings_by']
        price_by    = request.POST['price_by']
        searched    = request.POST['searched']
        ratings     = SendRatingNumerical(ratings_by)

        if price_by=="Low to high" and ratings!=6:
            title = Listing.objects.filter(rating__gte=ratings, exact_address__contains = searched, is_published=True, approved=True).order_by('price')
        elif price_by=="High to low" and ratings!=6:
            title = Listing.objects.filter( rating__gte=ratings,exact_address__contains = searched, is_published=True, approved=True).order_by('-price')
        elif price_by=="Low to high" and ratings==6:
            print("working")
            title = Listing.objects.filter(exact_address__contains = searched, is_published=True, approved=True).order_by('price')
        elif price_by=="High to low" and ratings==6:
            print("wORKING")
            title = Listing.objects.filter(exact_address__contains = searched, is_published=True, approved=True).order_by('-price')
        elif price_by=="------" and ratings!=6:
           title = Listing.objects.filter( rating__gte=ratings,exact_address__contains = searched, is_published=True, approved=True)

        else:
            title = Listing.objects.filter(exact_address__contains = searched, is_published=True, approved=True)
        
        paginator = Paginator(title, 10)
        return render(request, 'listings/searched_listings.html', {'searched': searched, 'posts': title} )

    else:
        
        return render(request, 'listings/searched_listings.html')

import branca
def map(request):

    object = Listing.objects.filter(approved=True)
    map     = folium.Map(location=[28.3974, 84], tiles="OpenStreetMap", zoom_start=7)
    for obj in object:
        lat, lng = float(obj.lat), float(obj.lng)
        if obj.is_published:
            status = "Running"
            col    = "Blue"
        else:
            status = "Not Running"
            col    = "Red"
        html = f"""
                <h3> {obj.title} </h3> 
                <p style="color: {col};">Status : {status}</p>
                <p>
                    Rating : {obj.rating}<br>
                    Price : {obj.price}<br>
                    Times Booked : {obj.total_bookings}<br>
                    City : {obj.city}<br>
                    Exact Location : {obj.exact_address}<br>
                    Host Details : {obj.user.full_name }</a>
                </p>
            """
        iframe = branca.element.IFrame(html=html, width=400, height=210)
        color   = "blue" if obj.is_published else "red" 
        popup = folium.Popup(iframe, max_width=500)
        folium.Marker(location=[lat, lng], popup= popup, tooltip="Click for More", parse_html=True, icon=folium.Icon(color=color)).add_to(map)
    map     = map._repr_html_()

    context = {
        'map' : map,
    }

    return render(request, "listings/map_listings.html", context)

def find_stars(star):
    if star > 0 and star < 0.5:
        stars = 0.5
    elif star > 0.5 and star < 1:
        stars = 1
    elif star > 1 and star < 1.5:
        stars = 1.5
    elif star > 1.5 and star < 2:
        stars = 2
    elif star > 2 and star < 2.5:
        stars = 2.5
    elif star > 2.5 and star < 3:
        stars = 3
    elif star > 3 and star < 3.5:
        stars = 3.5
    elif star > 3.5 and star < 4:
        stars = 4
    elif star > 4 and star < 4.5:
        stars = 4.5
    elif star > 4.5 and star < 5:
        stars = 5
    else :
        stars = star
    return stars

def contact_us(request):

    if request.method=="POST":
        form    =   ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "The information was submitted")
            return redirect(reverse('home'))
        else:
            messages.error(request, "The form was invalid. PLease heck and try again!")
            return redirect(reverse('contact-us'))
    else:
        form    = ContactUsForm()
        context = {
            'form' : form,
        }
        return render(request, "listings/contact_us.html", context)