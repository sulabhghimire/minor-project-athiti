from django.contrib import admin
from django.contrib.admin.decorators import register
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm
from .models import HostUser, GuestUser, Profile

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = ['email','full_name','admin', 'staff', 'host','guest',]
    list_filter = ['admin', 'staff', 'is_active', 'host', 'guest',]
    fieldsets = (
        (None, {'fields': ('full_name','email', 'country','state', 'phone_number','password')}),
        ('Permissions', {'fields': ('admin','staff', 'is_active', 'host','guest',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ['email', 'full_name', 'country', 'state', 'phone_number']
    ordering = ['email']
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(HostUser)
admin.site.register(GuestUser)
admin.site.register(Profile)

