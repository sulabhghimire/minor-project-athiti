from django.urls import path, include
from django.urls import path, include
from .views import CreateReport

urlpatterns = [
    path('send/<int:pk>', CreateReport, name='report')
]