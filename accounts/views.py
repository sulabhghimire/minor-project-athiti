from email import message
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from listings.models import Listing
from . forms import (
    GuestRegisterForm, HostRegisterForm, UserUpdateForm, ProfileUpdateForm, UserDeleteForm,
    EmailConformationResendForm
)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Profile
from review.models import RateGuest
from django.contrib.auth import login, authenticate, logout
from .models import EmailVerification, User
import uuid
from core import settings
import threading
from django.core.mail import send_mail
class EmailThread(threading.Thread):

    def __init__(self, mail_subject, to_mail, message, from_mail):
        self.mail_subject      = mail_subject
        self.to_mail           = to_mail
        self.message           = message
        self.from_mail         = from_mail 
        threading.Thread.__init__(self)

    def run(self):
        send_mail(subject = self.mail_subject, message = self.message, recipient_list = self.to_mail, 
        from_email =self.from_mail ,fail_silently=False)

def register_as_guest(request):

    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = GuestRegisterForm(request.POST)
            if form.is_valid():
                new_guest = form.save()
                uid = uuid.uuid4()
                verify_obj = EmailVerification(user=new_guest, token=uid)
                verify_obj.save()
                username = form.cleaned_data.get('username')
                mail_subject = 'Please Verify your guest account at Athiti'
                to_email = [new_guest.email]
                from_email = settings.EMAIL_HOST_USER
                message =  f'''Hi recently you have made a guest account in our platform Athiti.
                Please, click on the link given to verify your account.
                http://127.0.0.1:8000/account/verify/{uid}'''
                EmailThread(mail_subject, to_email, message, from_email ).start()
                messages.success(request, f'''Your account has been created as guest and an unique 
                token has been sent to your email address. Please verify your account.''')
            else:
                form = GuestRegisterForm()
                messages.warning(request, "Something wrong with your information. Please try again.")
                return render(request, 'accounts/guest_register.html', {'form': form})
        else:
            form = GuestRegisterForm()
            return render(request, 'accounts/guest_register.html', {'form': form})
    
    return redirect("home")

def register_as_host(request):

    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = HostRegisterForm(request.POST)
            if form.is_valid():
                new_host = form.save()
                uid = uuid.uuid4()
                verify_obj = EmailVerification(user=new_host, token=uid)
                verify_obj.save()
                mail_subject = 'Please Verify your guest account at Athiti'
                to_email = [new_host.email]
                from_email = settings.EMAIL_HOST_USER
                message =  f'''Hi recently you have made a host account in our platform Athiti.
                Please, click on the link given to verify your account.
                               http://127.0.0.1:8000/account/verify/{uid}'''
                EmailThread(mail_subject, to_email, message, from_email ).start()
                messages.success(request, f'''Your account has been created as host and an unique 
                token has been sent to your email address. Please verify your account.''')
                return redirect('home')
            else:
                form = HostRegisterForm()
                messages.warning(request, "Something wrong with your information. Please try again.")
                return render(request, 'accounts/host_register.html', {'form': form})
        else:
            form = HostRegisterForm()
            return render(request, 'accounts/host_register.html', {'form': form})


    return redirect("home")

def logout_view(request):

    if request.user.is_authenticated:
        logout(request)
        messages.success(request, f'You have been logged out from your account.')
        return redirect('home')
    else:
        return redirect("home")

@login_required
def profile_update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES, 
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            u_form.save()
            messages.success(request, f'Your account has been updated.')
            return redirect('profile', request.user.id)
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form' : u_form,
        'p_form' : p_form,
    }


    return render(request, 'accounts/update_profile.html', context)

def profile(request, pk):
    obj     = Profile.objects.get(id=pk)

    reviews = RateGuest.objects.filter(guest__id=pk, status=True)

    listings = Listing.objects.filter(is_published=True, approved=True, user=obj.user).order_by('-total_bookings') 

    if reviews: 
        star    = 0
        count   = 0
        for review in reviews:
            star    = star + review.rating
            count   = count + 1

        stars = find_stars(star/count)

        context = {
            'object' : obj,
            'reviews': reviews,
            'stars'  : stars, 
        }

        if listings:
            context = {
                'object' : obj,
                'reviews': reviews,
                'stars'  : stars,
                'posts'  : listings,    
            }
        
    else:
        context = {
            'object' : obj,
        }

        if listings:
            context = {
                'object'    : obj,
                'posts'     : listings,
            }

    return render(request, 'accounts/profile.html', context)
    
@login_required
def deleteuser(request):
    if request.method == 'POST':
        delete_form = UserDeleteForm(request.POST, instance=request.user)
        user = request.user
        user.delete()
        messages.info(request, 'Your account has been deleted.')
        return redirect('home')
    else:
        delete_form = UserDeleteForm(instance=request.user)

    context = {
        'delete_form' : delete_form
    }
    return render(request, 'accounts/delete_account.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated! Please login again.')
            logout(request)
            return redirect('login')
        else:
            messages.error(request, 'Error! Please try again.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/password_change.html', {
        'form': form
    })

def find_stars(star):
    if star > 0 and star < 0.5:
        stars = 0.5
    elif star > 0.5 and star < 1:
        stars = 1
    elif star > 1 and star < 1.5:
        stars = 1.5
    elif star > 1.5 and star < 2:
        stars = 2
    elif star > 2 and star < 2.5:
        stars = 2.5
    elif star > 2.5 and star < 3:
        stars = 3
    elif star > 3 and star < 3.5:
        stars = 3.5
    elif star > 3.5 and star < 4:
        stars = 4
    elif star > 4 and star < 4.5:
        stars = 4.5
    elif star > 4.5 and star < 5:
        stars = 5
    else :
        stars = star
    return stars


def log_in(request):

    if not request.user.is_authenticated:
        if request.method == "POST":
            form    = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    if user.emailverification.is_verified:
                        login(request, user)
                        messages.info(request, f"You have logged in as {username}.")
                        return redirect("home")
                    else:
                        messages.info(request, '''You haven't verified your email address yet.
                        Go to your email and check for verification mail. Also Check in junk folder.
                        If not found you can resend the verification mail.''')
                        return redirect("notverifiedemails")
                else:
                    messages.warning(request, "Invalid email or password.")
            else:
                messages.warning(request, "Invalid email or password.")

        form    = AuthenticationForm()
        context = {
            'form'  : form
        }
        return render(request, "accounts/login.html", context)
    
    else:
        return redirect("home")

def account_verify(request, token):

    try:
        object = EmailVerification.objects.get(token=token)
    except:
        object = None
    
    if object:
        if not object.is_verified:
            object.is_verified = True
            object.save()
            messages.success(request, "Your account has been verified. Now, you can login to your account.")
            return redirect('login')
        else:
            messages.info(request, "Your account was already verified.")
            return redirect('home')
    else:
        return redirect('home')

def not_verified(request):

    if request.method == "POST":
        form_data = EmailConformationResendForm(request.POST)
        if form_data.is_valid():
            email_address = form_data.cleaned_data.get('email_address')
            objects = User.objects.filter(email = email_address)
            if objects:
                for object in objects:
                    new_que = EmailVerification.objects.get(user = object)
                    if not new_que.is_verified:
                        resend_conformation_link(email_address, new_que)
                        messages.info(request, "We have resent conformation mail to your email address.")
                        return redirect("notverifiedemails")
                    else:
                        messages.info(request, "Your account with this email is already verified!")
                        return redirect('login')
            else:
                messages.info(request, "We don't any account registered with this email address.")
                return redirect("notverifiedemails")
        else:
            messages.warning(request, "Your email address isn't valid.")

    form = EmailConformationResendForm()
    context = {
        'form' : form,
    }

    return render(request, "accounts/not_verified_users.html", context)

def resend_conformation_link(email_address, object):
    uid = uuid.uuid4()
    object.token = uid
    object.save()
    if object.user.host:
        account_type = "host"
    if object.user.guest:
        account_type = "guest"
    mail_subject = f'Please Verify your {account_type} account at Athiti'
    to_email = [email_address]
    from_email = settings.EMAIL_HOST_USER
    message =  f'''Hi recently you have made a {account_type} account in our platform Athiti.
                This is new conformation mail being sent as per your request.
                Please, click on the link given to verify your account.
                http://127.0.0.1:8000/account/verify/{uid}'''
    EmailThread(mail_subject, to_email, message, from_email ).start()