from django import forms
from django.forms import fields
from .models import ReviewsAndRating, RateGuest

class ReviewForm(forms.ModelForm):

    class Meta:
        model       = ReviewsAndRating
        fields      = ['rating', 'review']

class GuestsReviewForm(forms.ModelForm):

    class Meta:
        model       = RateGuest
        fields      = ['rating', 'review']