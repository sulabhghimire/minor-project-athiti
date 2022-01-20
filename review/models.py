from django.db import models

from listings import views as listing_views
from django.contrib.auth import get_user_model

User = get_user_model()


class ReviewsAndRating(models.Model):

    room            = models.ForeignKey(listing_views.Listing, on_delete=models.CASCADE)
    reviewer        = models.ForeignKey(User, on_delete=models.CASCADE)
    review          = models.TextField(max_length=500, blank=True)
    rating          = models.FloatField()
    ip              = models.CharField(max_length=20, blank=True)
    status          = models.BooleanField(default=True)
    created_at      = models.DateField(auto_now_add=True)
    updated_at      = models.DateField(auto_now=True)

    def __str__(self):
        return f'Review of room {self.room} by {self.reviewer}.'

class RateGuest(models.Model):

    guest           = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Guest")
    host            = models.ForeignKey(User, on_delete=models.CASCADE, related_name="Host")
    review          = models.TextField(max_length=500, blank=True)
    rating          = models.FloatField()
    ip              = models.CharField(max_length=20, blank=True)
    status          = models.BooleanField(default=True)
    created_at      = models.DateField(auto_now_add=True)
    updated_at      = models.DateField(auto_now=True)

    def __str__(self):
        return f'Review of guest {self.guest} by {self.host}.'