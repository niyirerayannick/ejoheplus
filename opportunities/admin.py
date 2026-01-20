from django.contrib import admin
from .models import Opportunity, Application


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'created_by', 'deadline', 'is_active', 'created_at']
    list_filter = ['type', 'is_active', 'deadline']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'description']


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'opportunity', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['student__username', 'opportunity__title']
