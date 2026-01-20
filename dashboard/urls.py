from django.urls import path
from . import views
from . import api_views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('student/', views.student_dashboard, name='student_dashboard'),
    path('mentor/', views.mentor_dashboard, name='mentor_dashboard'),
    path('partner/', views.partner_dashboard, name='partner_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/create/', views.admin_user_create, name='admin_user_create'),
    path('admin/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('admin/users/<int:user_id>/delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin/mentors/', views.admin_mentors, name='admin_mentors'),
    path('admin/mentors/create/', views.admin_mentor_create, name='admin_mentor_create'),
    path('admin/mentors/<int:mentor_id>/edit/', views.admin_mentor_edit, name='admin_mentor_edit'),
    path('admin/mentors/<int:mentor_id>/delete/', views.admin_mentor_delete, name='admin_mentor_delete'),
    path('admin/mentors/<int:mentor_id>/assign/', views.admin_assign_mentor, name='admin_mentor_assign'),
    path('admin/mentors/assign/', views.admin_assign_mentor, name='admin_mentor_assign_general'),
    path('admin/mentor-approvals/', views.admin_mentor_approvals, name='admin_mentor_approvals'),
    path('admin/mentor-approvals/<int:mentor_id>/approve/', views.admin_mentor_approve, name='admin_mentor_approve'),
    path('admin/mentor-approvals/<int:mentor_id>/reject/', views.admin_mentor_reject, name='admin_mentor_reject'),
    path('admin/publications/', views.admin_publications, name='admin_publications'),
    path('admin/articles/', views.admin_articles, name='admin_articles'),
    path('admin/articles/create/', views.admin_article_create, name='admin_article_create'),
    path('admin/articles/<int:article_id>/edit/', views.admin_article_edit, name='admin_article_edit'),
    path('admin/articles/<int:article_id>/delete/', views.admin_article_delete, name='admin_article_delete'),
    path('admin/careers/', views.admin_careers, name='admin_careers'),
    path('admin/careers/create/', views.admin_career_create, name='admin_career_create'),
    path('admin/careers/<int:career_id>/edit/', views.admin_career_edit, name='admin_career_edit'),
    path('admin/careers/<int:career_id>/delete/', views.admin_career_delete, name='admin_career_delete'),
    path('admin/opportunities/', views.admin_opportunities, name='admin_opportunities'),
    path('admin/opportunities/create/', views.admin_opportunity_create, name='admin_opportunity_create'),
    path('admin/opportunities/<int:opportunity_id>/edit/', views.admin_opportunity_edit, name='admin_opportunity_edit'),
    path('admin/opportunities/<int:opportunity_id>/delete/', views.admin_opportunity_delete, name='admin_opportunity_delete'),
    path('admin/trainings/', views.admin_trainings, name='admin_trainings'),
    path('admin/trainings/create/', views.admin_training_create, name='admin_training_create'),
    path('admin/trainings/<int:training_id>/edit/', views.admin_training_edit, name='admin_training_edit'),
    path('admin/trainings/<int:training_id>/delete/', views.admin_training_delete, name='admin_training_delete'),
    path('admin/trainings/materials/', views.admin_materials, name='admin_materials'),
    path('admin/trainings/materials/create/', views.admin_material_create, name='admin_material_create'),
    path('admin/trainings/materials/<int:material_id>/edit/', views.admin_material_edit, name='admin_material_edit'),
    path('admin/trainings/materials/<int:material_id>/delete/', views.admin_material_delete, name='admin_material_delete'),
    path('admin/trainings/enrollments/', views.admin_enrollments, name='admin_enrollments'),
    path('admin/trainings/enrollments/create/', views.admin_enrollment_create, name='admin_enrollment_create'),
    path('admin/trainings/enrollments/<int:enrollment_id>/edit/', views.admin_enrollment_edit, name='admin_enrollment_edit'),
    path('admin/trainings/enrollments/<int:enrollment_id>/delete/', views.admin_enrollment_delete, name='admin_enrollment_delete'),
    path('admin/trainings/certificates/', views.admin_certificates, name='admin_certificates'),
    path('admin/trainings/certificates/create/', views.admin_certificate_create, name='admin_certificate_create'),
    path('admin/trainings/certificates/<int:certificate_id>/edit/', views.admin_certificate_edit, name='admin_certificate_edit'),
    path('admin/trainings/certificates/<int:certificate_id>/delete/', views.admin_certificate_delete, name='admin_certificate_delete'),
    path('admin/courses/', views.admin_trainings, name='admin_courses'),
    path('admin/courses/create/', views.admin_training_create, name='admin_course_create'),
    path('admin/courses/<int:training_id>/edit/', views.admin_training_edit, name='admin_course_edit'),
    path('admin/courses/<int:training_id>/delete/', views.admin_training_delete, name='admin_course_delete'),
    path('admin/courses/materials/', views.admin_materials, name='admin_course_materials'),
    path('admin/courses/materials/create/', views.admin_material_create, name='admin_course_material_create'),
    path('admin/courses/materials/<int:material_id>/edit/', views.admin_material_edit, name='admin_course_material_edit'),
    path('admin/courses/materials/<int:material_id>/delete/', views.admin_material_delete, name='admin_course_material_delete'),
    path('admin/courses/enrollments/', views.admin_enrollments, name='admin_course_enrollments'),
    path('admin/courses/enrollments/create/', views.admin_enrollment_create, name='admin_course_enrollment_create'),
    path('admin/courses/enrollments/<int:enrollment_id>/edit/', views.admin_enrollment_edit, name='admin_course_enrollment_edit'),
    path('admin/courses/enrollments/<int:enrollment_id>/delete/', views.admin_enrollment_delete, name='admin_course_enrollment_delete'),
    path('admin/courses/certificates/', views.admin_certificates, name='admin_course_certificates'),
    path('admin/courses/certificates/create/', views.admin_certificate_create, name='admin_course_certificate_create'),
    path('admin/courses/certificates/<int:certificate_id>/edit/', views.admin_certificate_edit, name='admin_course_certificate_edit'),
    path('admin/courses/certificates/<int:certificate_id>/delete/', views.admin_certificate_delete, name='admin_course_certificate_delete'),
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('profile/', views.profile, name='profile'),
    
    # CV Builder
    path('cv/', views.cv_builder, name='cv_builder'),
    path('cv/preview/', views.cv_preview, name='cv_preview'),
    
    # Messages / Chat
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/create/', views.message_create, name='message_create'),
    path('chat/<int:user_id>/', views.chat_detail, name='chat_detail'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/<int:message_id>/delete/', views.message_delete, name='message_delete'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete, name='notification_delete'),

    # Articles
    path('articles/', views.articles_list, name='articles_list'),
    path('articles/create/', views.article_create, name='article_create'),

    # Events
    path('events/', views.events_list, name='events_list'),
    path('events/create/', views.event_create, name='event_create'),

    # Mentor/Partner content creation
    path('courses/', views.courses_list, name='courses_list'),
    path('courses/<int:course_id>/manage/', views.course_manage, name='course_manage'),
    path('trainings/create/', views.training_create, name='training_create'),
    path('courses/create/', views.course_create, name='course_create'),
    path('opportunities/create/', views.opportunity_create, name='opportunity_create'),

    # Partner student management
    path('partner/students/', views.partner_students, name='partner_students'),
    path('partner/students/create/', views.partner_student_create, name='partner_student_create'),
    
    # Chat API endpoints for real-time updates
    path('api/chat/<int:user_id>/messages/', api_views.get_chat_messages, name='api_chat_messages'),
    path('api/chat/<int:user_id>/send/', api_views.send_message_api, name='api_send_message'),
    path('api/conversations/', api_views.get_conversations, name='api_conversations'),
]
