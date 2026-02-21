from django.contrib import admin
from .models import (
    Course,
    CourseMaterial,
    Enrollment,
    Certificate,
    CourseChapter,
    ChapterContent,
    Quiz,
    Question,
    Choice,
    QuizAttempt,
)


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


@admin.register(CourseChapter)
class CourseChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order']
    list_filter = ['course']
    ordering = ['course', 'order']


@admin.register(ChapterContent)
class ChapterContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'chapter', 'content_type', 'order']
    list_filter = ['content_type']
    ordering = ['chapter', 'order']


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'chapter', 'quiz_type', 'pass_score']
    list_filter = ['quiz_type', 'course']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'question_type']
    list_filter = ['question_type', 'quiz']
    inlines = [ChoiceInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'quiz', 'score', 'passed', 'completed_at']
    list_filter = ['passed', 'completed_at', 'quiz']
