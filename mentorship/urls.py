from django.urls import path
from . import views

app_name = 'mentorship'

urlpatterns = [
    path('', views.index, name='index'),
    path('mentors/', views.mentor_list, name='mentor_list'),
    path('mentor/<int:mentor_id>/', views.mentor_detail, name='mentor_detail'),
    path('mentor/<int:mentor_id>/request/', views.request_mentor, name='request_mentor'),
    
    # Mentor dashboard features
    path('mentor/mentees/', views.mentor_mentees, name='mentor_mentees'),
    path('mentor/mentee/<int:mentee_id>/', views.mentee_detail, name='mentee_detail'),
    path('mentor/connection/<int:connection_id>/accept/', views.accept_connection, name='accept_connection'),
    path('mentor/connection/<int:connection_id>/reject/', views.reject_connection, name='reject_connection'),
    
    path('mentor/sessions/', views.mentor_sessions, name='mentor_sessions'),
    path('mentor/sessions/create/', views.session_create, name='session_create'),
    path('mentor/sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('mentor/sessions/<int:session_id>/edit/', views.session_edit, name='session_edit'),
    path('mentor/sessions/<int:session_id>/complete/', views.session_complete, name='session_complete'),
    
    path('mentor/resources/', views.mentor_resources, name='mentor_resources'),
    path('mentor/resources/create/', views.resource_create, name='resource_create'),
    path('mentor/resources/<int:resource_id>/edit/', views.resource_edit, name='resource_edit'),
    path('mentor/resources/<int:resource_id>/delete/', views.resource_delete, name='resource_delete'),
    
    path('mentor/profile/edit/', views.mentor_profile_edit, name='mentor_profile_edit'),
]
