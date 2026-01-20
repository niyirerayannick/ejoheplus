"""
URL configuration for ejoheplus project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', core_views.home, name='home'),
    path('about/', core_views.about, name='about'),
    path('blog/', core_views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', core_views.blog_detail, name='blog_detail'),
    path('api/', include('core.api_urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('careers/', include('careers.urls')),
    path('opportunities/', include('opportunities.urls')),
    path('training/', include('training.urls')),
    path('courses/', include('training.course_urls')),
    path('mentorship/', include('mentorship.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
