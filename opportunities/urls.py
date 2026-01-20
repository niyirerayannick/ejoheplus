from django.urls import path
from . import views

app_name = 'opportunities'

urlpatterns = [
    path('', views.opportunity_list, name='list'),
    path('jobs/', views.jobs_page, name='jobs'),
    path('internships/', views.internships_page, name='internships'),
    path('scholarships/', views.scholarships_page, name='scholarships'),
    path('<slug:slug>/', views.opportunity_detail, name='detail'),
    path('<slug:slug>/apply/', views.apply, name='apply'),
]
