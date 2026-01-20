from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_mentor_approved', 'is_active', 'date_joined']
    list_filter = ['role', 'is_mentor_approved', 'is_active', 'date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('EjoHePlus Profile', {
            'fields': ('role', 'phone', 'profile_picture', 'bio', 'is_mentor_approved')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('EjoHePlus Profile', {
            'fields': ('role', 'phone', 'profile_picture', 'bio', 'is_mentor_approved')
        }),
    )
