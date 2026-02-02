from django.contrib import admin
from .models import (
    Career,
    CareerCategory,
    CareerProgram,
    CareerQuestion,
    CareerOption,
    CareerOptionWeight,
)


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'riasec_primary', 'riasec_secondary', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'overview']
    list_filter = ['category']


@admin.register(CareerCategory)
class CareerCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(CareerProgram)
class CareerProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'career', 'level', 'institution_type', 'country']
    search_fields = ['name', 'career__title']
    list_filter = ['level', 'institution_type', 'country']


class CareerOptionInline(admin.TabularInline):
    model = CareerOption
    extra = 1


@admin.register(CareerQuestion)
class CareerQuestionAdmin(admin.ModelAdmin):
    list_display = ['prompt', 'category', 'order', 'is_active']
    list_filter = ['category', 'is_active']
    ordering = ['order']
    inlines = [CareerOptionInline]


@admin.register(CareerOptionWeight)
class CareerOptionWeightAdmin(admin.ModelAdmin):
    list_display = ['option', 'career', 'weight']
    list_filter = ['career']