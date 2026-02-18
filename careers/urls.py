from django.urls import path
from . import views

app_name = 'careers'

urlpatterns = [
    path('', views.career_list, name='list'),
    path('discovery/', views.discovery_intro, name='discovery_intro'),
    path('discovery/questions/', views.discovery_questionnaire, name='discovery_questions'),
    path('discovery/history/', views.discovery_history, name='discovery_history'),
    path('discovery/results/', views.discovery_results, name='discovery_results'),
    path('<slug:slug>/', views.career_detail, name='detail'),
]
