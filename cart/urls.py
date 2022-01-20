from os import name
from django.conf.urls import url
from django.urls import path
from django.urls.resolvers import URLPattern

from .views import *

urlpatterns = [
    path('display/', cart_display, name='display_cart'),
    path('add_to_cart/<int:pk>', add_to_cart, name='add_to_cart'),
    path('delete_cart/<int:pk>', delete_cart, name='delete_cart'),
    path('generate_invoice/<int:pk>/<str:uid>', GenerateInvoice.as_view(), name='generate_invoice'),
    path('mail_invoice/<int:pk>/<str:uid>', MailInvoice.as_view(), name='send_invoice'),
]