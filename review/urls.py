from typing import Pattern
from django.urls import path
from . import views

urlpatterns = [
    path('post_review/<int:listing_id>/', views.RatingAndReviewListings, name='rate-and-review'),
    path('guest_review/<int:guest_id>/', views.RatingAndReviewGuests, name='rate-and-review-guest'),
]