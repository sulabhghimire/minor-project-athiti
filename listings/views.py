from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.template import context
from django.urls import reverse
from django.http.response import Http404
from markupsafe import re, string
from .forms import AvailabilityForm, ContactUsForm
import datetime
import folium
from . models import Listing, Booking, Refund_Control
import review.models as rev_model
import geocoder
from django.contrib.auth.decorators import user_passes_test
from django.views.generic import DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, AccessMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from listings.booking_functions.availability import check_availability
from listings.calculate_distance.distance import calculate_distance
from listings.calculate_distance.find_optimun import near_places
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

# Create your views here.

def CancelBooking(request, pk):

    if request.user.is_authenticated:
        obj                       = Booking.objects.get(id=pk)

        if obj.user_id == request.user.pk:
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

    return redirect('home')
    
def GuestViewsHostsListings(request, pk):

    user    = get_user_model().objects.get(id=pk)
    if not user.host:
        return redirect("home")
    objects = Listing.objects.filter(is_published=True, approved=True, user__id=pk)
    if len(objects) == 0:
        context = {
            'host_name' : user.full_name,
        }
    else:
        context = {
            'posts' : objects,
            'host_name' : user.full_name,
        }

    return render(request, 'listings/guest_look_host_listings.html', context)

class GuestsListingView(LoginRequiredMixin, ListView, AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.host == True:
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)
    
   
    model               = Booking
    template_name       = 'listings/guest_booking_info.html'
    context_object_name = 'posts'

class HostsListingView(LoginRequiredMixin, ListView, AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.guest == True:
            raise Http404
        return super().dispatch(request, *args, **kwargs)
    
    model               = Booking
    template_name       = 'listings/host_bookings_info.html'
    context_object_name = 'posts'
    
  
def home(request):
       
    url     = request.META.get('HTTP_REFERER')

    top_lisitngs = Listing.objects.filter(is_published=True, approved=True).order_by('-total_bookings')[:6]
    objects = Listing.objects.filter(is_published=True, approved=True).values(
        'lat', 'lng', 'title', 'description', 'exact_address', 'city', 'description', 'price', 'listing_type',
        'kitchen_available', 'kitchen_description', 'bedrooms', 'max_acomodation', 'bathroom_type', 'no_bathrooms',
        'room_type', 'main_photo', 'photo_1', 'photo_2', 'photo_3', 'rating', 'total_bookings', 'id',
    )
    g = geocoder.ip('me')
        
    for object in objects:

        lat, lng = float(object['lat']), float(object['lng'])
        object['distance'] = near_places(float(g.latlng[0]), float(g.latlng[1]), lat, lng)


        if object['main_photo'] == "default_room.jpg":
            initial_url          = object['main_photo']
            object['main_photo'] = "media/" + initial_url
        else:
            initial_url          = object['main_photo']
            object['main_photo'] = "media/" + initial_url

        if object['photo_1'] == "default_room.jpg":
            initial_url          = object['photo_1']
            object['photo_1']    = "media/" + initial_url
        else:
            initial_url          = object['photo_1']
            object['photo_1']    = "media/" + initial_url

        if object['photo_2'] == "default_room.jpg":
            initial_url          = object['photo_2']
            object['photo_2'] = "media/" + initial_url
        else:
            initial_url          = object['photo_2']
            object['photo_2'] = "media/" + initial_url

        if object['photo_3'] == "default_room.jpg":
            initial_url          = object['photo_3']
            object['photo_3'] = "media/" + initial_url
        else:
            initial_url          = object['photo_3']
            object['photo_3'] = "media/" + initial_url


    my_sorted_list = sorted(objects, key=lambda d: d['distance'], reverse=False)
    
    for object in my_sorted_list:

        object['distance'] = str(object['distance']) + " km"

    context = {
        'near_by_lisitngs' : my_sorted_list[:6],
        'top_lisitngs'     : top_lisitngs,
    }

    response =  render(request, 'listings/home.html', context)

    return response

    # if 'lat' in request.COOKIES and 'lng' in request.COOKIES:
    #     or_lat = float(request.COOKIES['lat'])
    #     or_lng = float(request.COOKIES['lng'])

    #     for object in objects:
    #         des_lat, des_lng = float(object['lat']), float(object['lng'])
    #         object['distance'] = near_places(or_lat, or_lng, des_lat, des_lng)
        
    #     my_sorted_list = sorted(objects, key=lambda k: k['distance'])
    #     context = {
    #         'posts' : my_sorted_list,
    #     }
    #     return render(request, 'listings/home.html', context)
    # else:
    #     g = geocoder.ip('me')
        
    #     for object in objects:
    #         lat, lng = float(object['lat']), float(object['lng'])
    #         object['distance'] = near_places(float(g.latlng[0]), float(g.latlng[1]), lat, lng)

    #     my_sorted_list = sorted(objects, key=lambda k: k['distance'])
    #     context = {
    #         'posts' : my_sorted_list,
    #     }
    #     print("Fetched")
    #     response =  render(request, 'listings/home.html')
        
    #     response.set_cookie('lat', g.latlng[0])
    #     response.set_cookie('lng', g.latlng[1])
    #     return response

def see_all_listings(request):

    lisitngs = Listing.objects.filter(is_published=True, approved=True).order_by('-total_bookings')

    page        = request.GET.get('page') 
    paginator = Paginator(lisitngs, 6)
    try:
        lisitngs = paginator.page(page)
    except PageNotAnInteger:
        lisitngs = paginator.page(1)
    except EmptyPage:
        lisitngs = paginator.page(paginator.num_pages)


    context = {
        'hosts' : lisitngs,
    }

    return render(request, 'listings/see_all_lisitngs.html', context)

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


def LisitngDetailView(request, pk):

    obj     = Listing.objects.get(id=pk, is_published=True, approved=True)
    reviews = rev_model.ReviewsAndRating.objects.filter(room_id=pk, status=True)
    map     = folium.Map(location=[28.3974, 84], tiles="OpenStreetMap", zoom_start=7)
    lat, lng = float(obj.lat), float(obj.lng)
    folium.Marker(location=[lat, lng], popup=obj.title, tooltip="Click for More").add_to(map)
    map     = map._repr_html_()
    distance = calculate_distance(lat, lng)
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
        'distance': distance,
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
            form = PostForm(request.POST, request.FILES, instance=listing)
            if form.is_valid():
                form.save()
                messages.success(request, "Your listing has been updated!")
                return redirect('listing-list')
            else:
                messages.warning(request, "Your form is invalid!")
                return redirect('listing-update', kwargs={'pk': pk})

        form    = PostForm(instance=listing)
        context = {
            'form'  : form,
            'post'  : listing,
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
            return True
        return False

def SearchTitle(request):

    def SendRatingNumerical(word):
        if word=="5":
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

    def SendPriceSearch(word):
        if word == "Low to high":
            return 1
        elif word == "High to low":
            return 2
        else:
            return 0

    page        = request.GET.get('page') 
    ratings_by  = request.GET.get('ratings_by')
    price       = request.GET.get('price_by')
    price_by    = SendPriceSearch(price)
    searched    = request.GET.get('searched')
    ratings     = SendRatingNumerical(ratings_by)


    if price_by==1 and ratings!=6:
        title = Listing.objects.filter(rating__gte=ratings, exact_address__contains = searched, is_published=True, approved=True).order_by('price')
    elif price_by==2 and ratings!=6:
        title = Listing.objects.filter( rating__gte=ratings,exact_address__contains = searched, is_published=True, approved=True).order_by('-price')
    elif price_by==1 and ratings==6:
        title = Listing.objects.filter(exact_address__contains = searched, is_published=True, approved=True).order_by('price')
    elif price_by==2 and ratings==6:
        title = Listing.objects.filter(exact_address__contains = searched, is_published=True, approved=True).order_by('-price')
    elif price_by==0 and ratings!=6:
       title = Listing.objects.filter( rating__gte=ratings,exact_address__contains = searched, is_published=True, approved=True)
    else:
        title = Listing.objects.filter(exact_address__contains = searched, is_published=True, approved=True)
    
    paginator = Paginator(title, 6)
    try:
        title = paginator.page(page)
    except PageNotAnInteger:
        title = paginator.page(1)
    except EmptyPage:
        title = paginator.page(paginator.num_pages)

    context = {
        'posts'         : title,
        'searched'      : searched,
        'rating_search' : ratings_by,
        'price_search'  : price,
    }
    return render(request, 'listings/searched_listings.html', context)


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
                    Host Details : {obj.user.full_name }<br>
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
            messages.warning(request, "The form was invalid. Please check and try again!")
            return redirect(reverse('contact-us'))
    else:
        form    = ContactUsForm()
        context = {
            'form' : form,
        }
        return render(request, "listings/contact_us.html", context)

from .utils import get_plot_pie, get_booking_details_bar, earning_details_bar
from .models import Booking
@user_passes_test(check_host)
def chart_view(request):

    year_dropdown = []
    for y in range(2021, (datetime.datetime.now().year)+1):
        year_dropdown.append(y)

    month_dropdown = ['Jan', 'Feb', 'Mar', 'April', 'May', 
                    'Jun', 'Jul', 'Aug' , 'Sept', 'Oct', 'Nov', 'Dec']

    corr_value = {
        'Jan' : '01', 
        'Feb' : '02', 
        'Mar' : '03', 
        'April' : '04',
        'May' : '05', 
        'Jun' : '06', 
        'Jul' : '07', 
        'Aug' : '08', 
        'Sept': '09', 
        'Oct' : '10', 
        'Nov' : '11', 
        'Dec' : '12',
    }

    graph_type  = request.GET.get('gtype')

    if graph_type == "bookings":
        object = Listing.objects.filter(user=request.user, is_published=True, approved=True)
        if object:
            x = [x.title for x in object]
            y = [y.total_bookings for y in object]
            chart = get_plot_pie(x,y)
            context = {
                'chart' : chart,
            }
            return render(request, 'listings/charts.html', context)

    elif graph_type == "earnings" or graph_type == None:

        if ((request.GET.get('year') == None )or (request.GET.get('year') == "")) or ((request.GET.get('month') == None) or (request.GET.get('month') == "")):
            
            check_year = str(datetime.date.today().year);
            check_mth = str(datetime.date.today().month);
            items = Booking.objects.filter(date_booked__year=check_year, 
                                                date_booked__month=check_mth,
                                                room_host_id = request.user.pk)
            items_count = len(items)
            booked_items = []
            cancelled_items = []
            completed_items =[]

            for item in items:
                if item.booking_progres=="Booked":
                    booked_items.append(item)
                elif item.booking_progres=="Cancelled":
                    cancelled_items.append(item)
                elif item.booking_progres=="Completed" :
                    completed_items.append(item)

            cancelled_count = len(cancelled_items)
            booked_count = len(booked_items)
            completed_count = len(completed_items)

            bar_graph_bookings_lables = ["Total", "Active", "Completed", "Cancelled"]
            bar_graph_bookings_values = [items_count, booked_count, completed_count, cancelled_count]

            this_month_booking_bar = get_booking_details_bar(bar_graph_bookings_lables, bar_graph_bookings_values, check_year, check_mth )

            rem_recieved_sum = 0
            rem_recieved_tax = 0
            rem_recieved_total = 0
            for item in booked_items:
                rem_recieved_sum += item.sum_amount
                rem_recieved_tax += item.tax_amount
                rem_recieved_total += rem_recieved_sum + rem_recieved_tax

            completed_recieved_sum = 0
            completed_recieved_tax = 0
            completed_total = 0
            for item in completed_items:
                completed_recieved_sum += item.sum_amount
                completed_recieved_tax += item.tax_amount
                completed_total += completed_recieved_sum + completed_recieved_tax

            labels = ["Remaining", "Recieved"]
            y_first = [rem_recieved_total, completed_total]
            y_second = [rem_recieved_tax, completed_recieved_tax]
            y_third = [rem_recieved_sum, completed_recieved_sum]

            earning_bar = earning_details_bar(labels, y_first, y_second, y_third, check_year, check_mth)

            context = {
            'graph_type' : "Value",
            'year_dropdown' : year_dropdown,
            'month_dropdown' : month_dropdown,
            'items_count' : items_count,
            'cancelled_count' : cancelled_count,
            'booked_count' : booked_count,
            'completed_count' : completed_count,
            'this_month_booking_bar' : this_month_booking_bar,
            'earning_bar' : earning_bar,
            }


            return render(request, 'listings/charts.html', context)
        else:
            check_year = request.GET.get('year')
            check_mth = request.GET.get('month') 

            curr_year = datetime.date.today().year;
            curr_mth = datetime.date.today().month;

            if curr_year <= int(check_year):
                if curr_mth <= curr_mth:
                    print("yes")

            if check_mth in corr_value.keys():

                items = Booking.objects.filter(date_booked__year=check_year, 
                                                date_booked__month=corr_value[check_mth],
                                                room_host_id = request.user.pk)
                items_count = len(items)

                booked_items = []
                cancelled_items = []
                completed_items =[]

                for item in items:
                    if item.booking_progres=="Booked":
                        booked_items.append(item)
                    elif item.booking_progres=="Cancelled":
                        cancelled_items.append(item)
                    elif item.booking_progres=="Completed" :
                        completed_items.append(item)

                cancelled_count = len(cancelled_items)
                booked_count = len(booked_items)
                completed_count = len(completed_items)
                
                bar_graph_bookings_lables = ["Total", "Active", "Completed", "Cancelled"]
                bar_graph_bookings_values = [items_count, booked_count, completed_count, cancelled_count]

                this_month_booking_bar = get_booking_details_bar(bar_graph_bookings_lables, bar_graph_bookings_values, check_year, corr_value[check_mth] )

                rem_recieved_sum = 0
                rem_recieved_tax = 0
                rem_recieved_total = 0
                for item in booked_items:
                    rem_recieved_sum += item.sum_amount
                    rem_recieved_tax += item.tax_amount
                    rem_recieved_total += rem_recieved_sum + rem_recieved_tax

                completed_recieved_sum = 0
                completed_recieved_tax = 0
                completed_total = 0
                for item in completed_items:
                    completed_recieved_sum += item.sum_amount
                    completed_recieved_tax += item.tax_amount
                    completed_total += completed_recieved_sum + completed_recieved_tax

                labels = ["Remaining", "Recieved"]
                y_first = [rem_recieved_total, completed_total]
                y_second = [rem_recieved_tax, completed_recieved_tax]
                y_third = [rem_recieved_sum, completed_recieved_sum]

                earning_bar = earning_details_bar(labels, y_first, y_second, y_third, check_year, corr_value[check_mth])

                context = {
                'graph_type' : "Value",
                'year_dropdown' : year_dropdown,
                'month_dropdown' : month_dropdown,
                'items_count' : items_count,
                'cancelled_count' : cancelled_count,
                'booked_count' : booked_count,
                'completed_count' : completed_count,
                'this_month_booking_bar' : this_month_booking_bar,
                'earning_bar' : earning_bar,
                }


                return render(request, 'listings/charts.html', context)

            else:
                messages.info(request, "Please give month correctly!")
    
    context = {
        'graph_type' : "Value",
        'year_dropdown' : year_dropdown,
        'month_dropdown' : month_dropdown,
    }
    return render(request, 'listings/charts.html', context)

    
