from django.shortcuts import render, redirect
from django.contrib import messages

from listings.models import Listing
from . forms import GuestRegisterForm, HostRegisterForm, UserUpdateForm, ProfileUpdateForm, UserDeleteForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Profile
from review.models import RateGuest

def register_as_guest(request):

    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = GuestRegisterForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Your account has been created as guest you can login.')
                return redirect('home')
        else:
            form = GuestRegisterForm()

        return render(request, 'accounts/guest_register.html', {'form': form})
    else:
        return redirect("home")

def register_as_host(request):

    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = HostRegisterForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Your account has been created as host now you can login.')
                return redirect('home')
        else:
            form = HostRegisterForm()

        return render(request, 'accounts/host_register.html', {'form': form})

    else:
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