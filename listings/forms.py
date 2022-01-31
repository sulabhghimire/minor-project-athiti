from email.message import Message
from operator import mod
from pyexpat import model
from django import forms
from .models import Listing, Contact

class AvailabilityForm(forms.Form):
    room_name   = forms.IntegerField(required=True)
    check_in    = forms.DateField(required=True, input_formats=['%Y-%m-%d'])
    check_out   = forms.DateField(required=True, input_formats=['%Y-%m-%d'])

class PostForm(forms.ModelForm):
    
    class Meta:

        model       = Listing
        fields      = (
            'title', 
            'city',
            'exact_address',
            'lat',
            'lng',
            'description',
            'price',
            'listing_type',
            'kitchen_available',
            'kitchen_description',
            'bedrooms',
            'max_acomodation',
            'bathroom_type',
            'no_bathrooms',
            'room_type',
            'main_photo',
            'photo_1',
            'photo_2',
            'photo_3',
            'is_published',
        )

class ContactUsForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = (
            'full_name',
            'Email', 
            'Phone_Number', 
            'Message',
        )

    