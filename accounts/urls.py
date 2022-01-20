from django.contrib import messages
from . import views
from . import models
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('guest_register/', views.register_as_guest, name='guest-register'),
    path('host_register/', views.register_as_host, name='host-register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<int:pk>/', views.profile, name='profile'),
    path('profile_update/', views.profile_update, name='profile-update'),
    path('delete_account/', views.deleteuser, name='delete-account'),
    path('password_change/', views.change_password, name='password-change'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]