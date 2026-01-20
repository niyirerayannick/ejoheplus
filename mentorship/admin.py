from django.contrib import admin
from .models import MentorshipConnection, MentorshipSession, MentorResource, MentorProfile


@admin.register(MentorshipConnection)
class MentorshipConnectionAdmin(admin.ModelAdmin):
    list_display = ['mentor', 'mentee', 'status', 'requested_at', 'accepted_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['mentor__username', 'mentee__username']
    readonly_fields = ['requested_at']


@admin.register(MentorshipSession)
class MentorshipSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'connection', 'scheduled_date', 'status', 'duration_minutes']
    list_filter = ['status', 'scheduled_date']
    search_fields = ['title', 'connection__mentor__username', 'connection__mentee__username']
    date_hierarchy = 'scheduled_date'


@admin.register(MentorResource)
class MentorResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'mentor', 'resource_type', 'is_public', 'created_at']
    list_filter = ['resource_type', 'is_public', 'created_at']
    search_fields = ['title', 'mentor__username']
    filter_horizontal = ['connections']


@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ['mentor', 'professional_title', 'company', 'max_mentees', 'current_mentee_count']
    search_fields = ['mentor__username', 'professional_title', 'company']
