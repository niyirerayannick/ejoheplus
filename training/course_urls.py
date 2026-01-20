from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.learning_dashboard, name='learning_dashboard'),
    path('create/', views.course_create, name='course_create'),
    path('<slug:slug>/manage/', views.course_manage, name='course_manage'),
    path('<slug:slug>/chapters/add/', views.chapter_create, name='chapter_create'),
    path('chapters/<int:chapter_id>/edit/', views.chapter_edit, name='chapter_edit'),
    path('chapters/<int:chapter_id>/delete/', views.chapter_delete, name='chapter_delete'),
    path('chapters/<int:chapter_id>/contents/add/', views.content_create, name='content_create'),
    path('contents/<int:content_id>/edit/', views.content_edit, name='content_edit'),
    path('contents/<int:content_id>/delete/', views.content_delete, name='content_delete'),
    path('<slug:slug>/quizzes/add/', views.quiz_create, name='quiz_create'),
    path('<slug:slug>/chapters/<int:chapter_id>/quizzes/add/', views.quiz_create, name='chapter_quiz_create'),
    path('quizzes/<int:quiz_id>/edit/', views.quiz_edit, name='quiz_edit'),
    path('quizzes/<int:quiz_id>/delete/', views.quiz_delete, name='quiz_delete'),
    path('quizzes/<int:quiz_id>/questions/add/', views.question_create, name='question_create'),
    path('questions/<int:question_id>/edit/', views.question_edit, name='question_edit'),
    path('questions/<int:question_id>/delete/', views.question_delete, name='question_delete'),
    path('questions/<int:question_id>/choices/add/', views.choice_create, name='choice_create'),
    path('choices/<int:choice_id>/delete/', views.choice_delete, name='choice_delete'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    path('<slug:slug>/enroll/', views.enroll, name='enroll'),
    path('<slug:slug>/learn/', views.course_learn, name='course_learn'),
    path('chapters/<int:chapter_id>/complete/', views.mark_chapter_complete, name='chapter_complete'),
    path('quizzes/<int:quiz_id>/take/', views.take_quiz, name='take_quiz'),
    path('<slug:slug>/certificate/', views.download_certificate, name='download_certificate'),
]
