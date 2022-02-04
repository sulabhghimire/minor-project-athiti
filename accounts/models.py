from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, UserManager
)
from django_countries.fields import CountryField
from django.utils import timezone

from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms.fields import ImageField
from PIL import Image

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, country, state, phone_number, password=None, active=True):
        if not email:
            raise ValueError("Users must have an email address")
        if not password:
            raise ValueError("Users must have passwords")
        if not full_name:
            raise ValueError("Users must have fullname")

        user = self.model(
            email           = self.normalize_email(email).lower(),
            full_name       = full_name,
            country         = country,
            state           = state,
            phone_number    = phone_number,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, full_name, country, state, phone_number, password):
        user = self.create_user(
            email,
            full_name,
            country,
            state,
            phone_number,
            password=password,
        )
        user.staff=True
        user.save(using=self._db)
        return user


    def create_superuser(self, email, full_name,country, state, phone_number, password):
        user = self.create_user(
            email,
            full_name,
            country,
            state,
            phone_number,
            password=password,
        )
        user.staff=True
        user.admin=True
        user.save(using=self._db)
        return user

    def create_guestuser(self, email,full_name,country, state, phone_number, password):
        user = self.create_user(
            email,
            full_name,
            country,
            state,
            phone_number,
            password=password,
        )
        user.guest=True
        user.save(using=self._db)
        return user

    def create_hostuser(self, email,full_name,country, state, phone_number, password):
        user = self.create_user(
            email,
            full_name,
            country,
            state,
            phone_number,
            password=password,
        )
        user.host=True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email       = models.EmailField(max_length=255, unique=True)
    is_active   = models.BooleanField(default=True)
    staff       = models.BooleanField(default=False)
    admin       = models.BooleanField(default=False)
    host        = models.BooleanField(default=False)
    guest       = models.BooleanField(default=False)
    timestamp   = models.DateTimeField(default=timezone.now, editable=False)
    full_name   = models.CharField(max_length=255, blank=False, unique=False)
    country     = CountryField(blank_label='(Select Country)')
    state       = models.CharField(max_length=255, blank=False)
    phone_number = models.PositiveIntegerField(unique=True, blank=True, validators=[MaxValueValidator(9999999999), MinValueValidator(9000000000)], default=0000000000,error_messages={'required': 'Enter a valid phone number'})
    
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['full_name', 'country', 'state', 'phone_number']

    objects = UserManager()

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.email

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_admin(self):
        return self.admin

    @property
    def is_host(self):
        return self.host

    @property
    def is_guest(self):
        return self.guest

class Profile(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE)
    image   = models.ImageField(default='default_profile.png', upload_to='profile_pics')

    def __str__(self):
        return f'{self.user.full_name} | {self.user.email}'

    def save(self, *args, **kwargs):
        super().save( *args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

        try:
            this = Profile.objects.get(id=self.id)
            if this.image != self.image:
                this.image.delete()
        except: 
            pass

class GuestUser(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE)
    ratings = models.DecimalField(max_digits=3, decimal_places=2, default=5)

    def __str__(self):
        return self.user.email

class HostUser(models.Model):
    user    = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email
