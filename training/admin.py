from django.contrib import admin
from .models import Course, CourseMaterial, Enrollment, Certificate


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'level', 'is_free', 'is_active', 'created_at']
    list_filter = ['level', 'is_free', 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'description']


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'material_type', 'order']
    list_filter = ['material_type']
    ordering = ['course', 'order']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'is_completed']
    list_filter = ['is_completed', 'enrolled_at']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_id', 'enrollment', 'issued_at']
