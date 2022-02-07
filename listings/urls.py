from django.db.models.base import Model
from django.urls import path
from jason import view
from . import views
from . import models

urlpatterns = [
    path('', views.home, name='home'),
    path('search_listings', views.SearchTitle, name='search'),
    path('host_listings/', views.ListListings.as_view(), name='listing-list'),
    path('listing_details/<int:pk>/', views.LisitngDetailView, name='listing-details'),
    path('listing_details/<int:pk>/update/', views.update_item, name='listing-update'),
    path('listing_details/<int:pk>/delete/', views.ListingDelete.as_view(), name='listing-delete'),
    path('post_listing/', views.post_item, name='listing-post'),
    path('your_bookings/', views.GuestsListingView.as_view(), name='guests-booking'),
    path('booked_rooms/', views.HostsListingView.as_view(), name='hosts-booking'),
    path('cancel-booking/<int:pk>/', views.CancelBooking, name='cancel-booking'),
    path('check-avaibality/', views.CheckRoomAvabiality, name='check-avaibality'),
    path('all_locations/', views.map, name="map"),
    path('contact-us/', views.contact_us, name="contact-us"),
    path('view-hosts-listings/<int:pk>', views.GuestViewsHostsListings, name="host-lisitngs"),
    path('all_listings/', views.see_all_listings, name='lisitngs'),
]