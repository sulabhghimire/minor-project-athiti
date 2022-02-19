from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.db import transaction
from django.contrib.auth.forms import UserCreationForm
from django.forms import fields

from accounts.models import GuestUser, HostUser, Profile


User = get_user_model()

class EmailConformationResendForm(forms.Form):

    email_address = forms.EmailField(max_length=255, required=True)

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['full_name','email', 'country', 'state', 'phone_number']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_2 = cleaned_data.get("password_2")
        if password is not None and password != password_2:
            self.add_error("password_2", "Your passwords must match")
        return cleaned_data


class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        fields = ['full_name','email', 'country', 'state', 'phone_number']
        model= User

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords don\'t match')
        return password2

    def save(self, commit=True):
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email','full_name', 'password', 'is_active', 'admin', 'country', 'state', 'phone_number']

    def clean_password(self):
        return self.initial["password"]

class GuestRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'full_name',
            'email',
            'country', 
            'state', 
            'phone_number',
            'password1', 
            'password2',
        ]

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.guest=True
        user.save()
        guest = GuestUser.objects.create(user=user)
        guest.save()
        return user
    
class HostRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'full_name',
            'email',
            'country', 
            'state', 
            'phone_number',
            'password1', 
            'password2'
        ]

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.host=True
        user.save()
        host = HostUser.objects.create(user=user)
        host.save()
        return user
    
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'full_name',
            'country',
            'state',
        ]

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

class UserDeleteForm(forms.ModelForm):
    class Meta:
        model = User
        fields = []