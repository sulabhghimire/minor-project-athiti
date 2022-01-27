


from django.db import models
from django.contrib.auth import get_user_model
from django_extensions.db.fields import AutoSlugField
import uuid
from accounts.forms import User
from PIL import Image

User = get_user_model()

class RoomLocation(models.Model):
    location_city       = models.CharField(max_length=100)

    def __str__(self):
        return self.location_city

class Listing(models.Model):

    class BathRoomType(models.TextChoices):
        ATTACHED = 'Attached Bathroom'
        COMMON   = 'Shared Bathroom'
    
    class RoomVentType(models.TextChoices):
        AC      = 'Air Conditioner'
        NO_AC   = 'No Air Conditioner'

    class LisitngType(models.TextChoices):
        ROOM        = 'Room'
        APARTEMENT  = 'Apartement'
        HOUSE       =  'Full House'
    
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    title               = models.CharField(max_length=255)
    city                = models.ForeignKey(RoomLocation, on_delete=models.CASCADE)
    exact_address       = models.CharField(max_length=255)
    lat                 = models.CharField(max_length=30, null=True)
    lng                 = models.CharField(max_length=30, null=True)
    description         = models.TextField()
    price               = models.IntegerField()
    listing_type        = models.CharField(max_length=20, choices=LisitngType.choices, default=LisitngType.ROOM)
    kitchen_available   = models.BooleanField(default=False)
    kitchen_description = models.TextField()
    bedrooms            = models.IntegerField()
    max_acomodation     = models.IntegerField()
    bathroom_type       = models.CharField(max_length=20, choices=BathRoomType.choices, default=BathRoomType.ATTACHED)
    no_bathrooms        = models.IntegerField()
    room_type           = models.CharField(max_length=30, choices=RoomVentType.choices, default=RoomVentType.AC)
    main_photo          = models.ImageField(upload_to='room_images', default='default_room.jpg')
    photo_1             = models.ImageField(upload_to='room_images', default='default_room.jpg')
    photo_2             = models.ImageField(upload_to='room_images', default='default_room.jpg')
    photo_3             = models.ImageField(upload_to='room_images', default='default_room.jpg')
    is_published        = models.BooleanField(default=False)
    date_created        = models.DateTimeField(auto_now_add=True)
    slug                = AutoSlugField(populate_from=['title', 'listing_type', 'bathroom_type', 'room_type'])
    rating              = models.IntegerField(default=5)
    approved            = models.BooleanField(default=False)
    total_bookings      = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save( *args, **kwargs)

        main_photo_     =   Image.open(self.main_photo)
        photo_1_        =   Image.open(self.photo_1)
        photo_2_        =   Image.open(self.photo_2)
        photo_3_        =   Image.open(self.photo_3)
        output_size = (600, 600)

    
        main_photo_.thumbnail(output_size)
        main_photo_.save(self.main_photo.path)
        photo_1_.thumbnail(output_size)
        photo_1_.save(self.photo_1.path)
        photo_2_.thumbnail(output_size)
        photo_2_.save(self.photo_2.path)
        photo_3_.thumbnail(output_size)
        photo_3_.save(self.photo_3.path)

        try:
            this = Listing.objects.get(id=self.id)
            if this.main_photo != self.main_photo:
                this.main_photo.delete()
            if this.photo_1 != self.photo_1:
                this.photo_1.delete()
            if this.photo_2 != self.photo_2:
                this.photo_1.delete()
            if this.photo_3 != self.photo_3:
                this.photo_3.delete()   
        except:
            pass

    class Meta:
        ordering = ['approved']

class Booking(models.Model):

    uuid                    = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    idx                     = models.CharField(max_length=100)
    date_booked             = models.DateField(auto_now_add=True)
    user_id                 = models.IntegerField()
    user_email              = models.EmailField(max_length=100,unique=False) 
    user_full_name          = models.CharField(max_length=100)
    room_host_id            = models.IntegerField()
    room_host_full_name     = models.CharField(max_length=100)
    room_host_email         = models.EmailField(max_length=100, unique=False)
    room_host_phone         = models.IntegerField()
    room_id                 = models.IntegerField()
    room_city               = models.CharField(max_length=100)
    room_exact_address      = models.CharField(max_length=100)
    check_in                = models.DateField()
    check_out               = models.DateField()
    sum_amount              = models.DecimalField(max_digits=10, decimal_places=3)
    tax_amount              = models.DecimalField(max_digits=10, decimal_places=3)
    service_charge_amount   = models.DecimalField(max_digits=10, decimal_places=3)
    total_amount            = models.DecimalField(max_digits=10, decimal_places=3)
    booking_progres         = models.CharField(max_length=20, default='Booked')
    refund_status           = models.CharField(max_length=100, default='None')

    class Meta:
        ordering = ['check_in']

    def __str__(self):
        return f'{self.user_full_name} has booked {self.room_city} from {self.check_in} to {self.check_out} of {self.room_host_email}.'

class Refund_Control(models.Model):

    booking_staus           = models.OneToOneField(Booking, on_delete=models.CASCADE)
    sum_amount              = models.DecimalField(max_digits=10, decimal_places=3)
    tax_amount              = models.DecimalField(max_digits=10, decimal_places=3)
    service_charge_amount   = models.DecimalField(max_digits=10, decimal_places=3)
    total_amount            = models.DecimalField(max_digits=10, decimal_places=3)
    refund_percentage       = models.CharField(max_length=3, default=' ')
    refund_completed        = models.BooleanField(default=False)

    class Meta:
        ordering = ['refund_completed']

    def __str__(self):
        return f'{self.booking_staus.user_full_name} has to recieve {self.refund_percentage}% refund.'

class Contact(models.Model):
    full_name       = models.CharField(max_length=30,blank=False)
    Email           = models.EmailField(blank=False, max_length=255, unique=False)
    Phone_Number    = models.CharField(blank=True, max_length=10)
    Message         = models.TextField(blank=False)

    def __str__(self):
        return f'{self.Email} with name {self.full_name} has sent message.'

