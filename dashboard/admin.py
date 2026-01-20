from django.contrib import admin
from .models import StudentCV, Message, Notification


@admin.register(StudentCV)
class StudentCVAdmin(admin.ModelAdmin):
    list_display = ['student', 'full_name', 'email', 'updated_at']
    search_fields = ['student__username', 'full_name', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'recipient', 'subject', 'has_attachment', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['sender__username', 'recipient__username', 'subject', 'attachment_name']
    readonly_fields = ['attachment_size']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'title', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
