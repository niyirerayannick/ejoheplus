from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import User
from .forms import LoginForm, RegisterForm, ProfileUpdateForm


def login_view(request):
    """User login view with persistent session"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # Try to authenticate with email
            try:
                user = User.objects.get(email=email)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                user = None
            
            if user is not None:
                login(request, user)
                remember_me = form.cleaned_data.get('remember_me')
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                # Redirect based on role
                if user.is_administrator:
                    return redirect('dashboard:admin_dashboard')
                elif user.is_mentor:
                    return redirect('dashboard:mentor_dashboard')
                elif user.is_partner:
                    return redirect('dashboard:partner_dashboard')
                else:
                    return redirect('dashboard:student_dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'auth/login.html', {'form': form})


def register_view(request):
    """User registration view with role selection"""
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    initial_role = request.GET.get('role', 'student')
    if initial_role not in ['student', 'mentor', 'partner']:
        initial_role = 'student'
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            # Auto-approve students and partners, mentors need approval
            if user.role == 'student' or user.role == 'partner':
                user.is_mentor_approved = True
                user.save()
            
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('accounts:login')
    else:
        form = RegisterForm(initial={'role': initial_role})
    
    return render(request, 'auth/register.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('dashboard:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    context = {
        'page_title': 'Edit Profile',
        'form': form,
    }
    return render(request, 'auth/profile_edit.html', context)
