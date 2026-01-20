from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views
from .forms import StyledPasswordResetForm, StyledSetPasswordForm, StyledPasswordChangeForm

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset_form.html',
        form_class=StyledPasswordResetForm,
        email_template_name='auth/password_reset_email.html',
        subject_template_name='auth/password_reset_subject.txt',
        success_url=reverse_lazy('accounts:password_reset_done')
    ), name='password_reset'),
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('password/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        form_class=StyledSetPasswordForm,
        success_url=reverse_lazy('accounts:password_reset_complete')
    ), name='password_reset_confirm'),
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('password/change/', auth_views.PasswordChangeView.as_view(
        template_name='auth/password_change_form.html',
        form_class=StyledPasswordChangeForm,
        success_url=reverse_lazy('accounts:password_change_done')
    ), name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='auth/password_change_done.html'
    ), name='password_change_done'),
]
