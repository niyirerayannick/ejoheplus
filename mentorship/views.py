from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import User
from careers.models import CareerDiscoveryResponse, CareerOptionWeight, Career
from django.db.models import Prefetch
from dashboard.models import Notification
from .models import MentorshipConnection, MentorshipSession, MentorResource, MentorProfile
from .forms import SessionForm, ResourceForm, MentorProfileForm


def index(request):
    """Mentorship index page"""
    context = {
        'page_title': 'Mentorship',
    }
    return render(request, 'mentorship/index.html', context)


@login_required
def mentor_list(request):
    """List of available mentors"""
    mentors = User.objects.filter(role='mentor', is_mentor_approved=True).select_related('mentor_profile').prefetch_related(
        'mentor_profile__career_categories',
        'mentor_profile__career_focuses',
    )

    category_filter = request.GET.get('category', '').strip()
    level_filter = request.GET.get('level', '').strip()

    if category_filter:
        mentors = mentors.filter(mentor_profile__career_categories__slug=category_filter).distinct()

    if level_filter:
        mentors = mentors.filter(mentor_profile__student_levels__icontains=level_filter).distinct()

    recommended = []
    if request.user.is_authenticated and request.user.is_student and not category_filter and not level_filter:
        session_key = request.session.session_key
        if session_key:
            latest_response = CareerDiscoveryResponse.objects.filter(session_key=session_key).order_by('-created_at').first()
            if latest_response:
                weights = CareerOptionWeight.objects.filter(option__careerdiscoveryanswer__response=latest_response).select_related('career')
                scores = {}
                for weight in weights:
                    scores[weight.career_id] = scores.get(weight.career_id, 0) + weight.weight
                top_career_ids = sorted(scores, key=scores.get, reverse=True)[:5]
                recommended = mentors.filter(
                    mentor_profile__career_focuses__id__in=top_career_ids
                ).distinct()[:6]

    categories = mentors.values_list('mentor_profile__career_categories__name', 'mentor_profile__career_categories__slug').distinct()
    categories = [{'name': name, 'slug': slug} for name, slug in categories if name and slug]

    context = {
        'page_title': 'Find a Mentor',
        'mentors': mentors,
        'recommended_mentors': recommended,
        'categories': categories,
        'active_category': category_filter,
        'active_level': level_filter,
    }
    return render(request, 'mentorship/mentor_list.html', context)


@login_required
def mentor_detail(request, mentor_id):
    """Mentor profile details for students"""
    mentor = get_object_or_404(User, id=mentor_id, role='mentor', is_mentor_approved=True)
    profile = MentorProfile.objects.filter(mentor=mentor).first()
    connection = None
    if request.user.is_student:
        connection = MentorshipConnection.objects.filter(mentor=mentor, mentee=request.user).first()

    context = {
        'page_title': f'{mentor.get_full_name() or mentor.username} - Mentor Profile',
        'mentor': mentor,
        'profile': profile,
        'connection': connection,
    }
    return render(request, 'mentorship/mentor_detail.html', context)


@login_required
def request_mentor(request, mentor_id):
    """Student sends a mentorship request"""
    if not request.user.is_student:
        messages.error(request, 'Only students can request mentorship.')
        return redirect('dashboard:index')

    mentor = get_object_or_404(User, id=mentor_id, role='mentor', is_mentor_approved=True)
    if mentor == request.user:
        messages.error(request, 'You cannot request mentorship from yourself.')
        return redirect('mentorship:mentor_detail', mentor_id=mentor.id)

    connection, created = MentorshipConnection.objects.get_or_create(
        mentor=mentor,
        mentee=request.user,
        defaults={'status': 'pending'}
    )
    if created:
        Notification.objects.create(
            user=mentor,
            notification_type='mentorship_request',
            title='New Mentorship Request',
            message=f'{request.user.get_full_name() or request.user.username} sent you a mentorship request.',
            related_url='/mentorship/mentor/mentees/'
        )
        messages.success(request, 'Mentorship request sent successfully.')
    else:
        messages.info(request, 'You already have a mentorship request with this mentor.')

    return redirect('mentorship:mentor_detail', mentor_id=mentor.id)


@login_required
def mentor_mentees(request):
    """Mentor's mentees list"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can access this page.')
        return redirect('dashboard:index')
    
    connections = MentorshipConnection.objects.filter(
        mentor=request.user,
        status='accepted'
    ).select_related('mentee').order_by('-accepted_at')
    
    pending_requests = MentorshipConnection.objects.filter(
        mentor=request.user,
        status='pending'
    ).select_related('mentee').order_by('-requested_at')
    
    context = {
        'page_title': 'My Mentees',
        'connections': connections,
        'pending_requests': pending_requests,
    }
    return render(request, 'mentorship/mentor_mentees.html', context)


@login_required
def mentee_detail(request, mentee_id):
    """View mentee profile details"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can access this page.')
        return redirect('dashboard:index')
    
    mentee = get_object_or_404(User, id=mentee_id, role='student')
    connection = MentorshipConnection.objects.filter(
        mentor=request.user,
        mentee=mentee
    ).first()
    
    # Get sessions with this mentee
    if connection:
        sessions = MentorshipSession.objects.filter(connection=connection).order_by('-scheduled_date')
    else:
        sessions = []
    
    context = {
        'page_title': f'{mentee.get_full_name() or mentee.username} - Profile',
        'mentee': mentee,
        'connection': connection,
        'sessions': sessions,
    }
    return render(request, 'mentorship/mentee_detail.html', context)


@login_required
def accept_connection(request, connection_id):
    """Accept a mentorship connection request"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can accept requests.')
        return redirect('dashboard:index')
    
    connection = get_object_or_404(MentorshipConnection, id=connection_id, mentor=request.user)
    
    if connection.status == 'pending':
        connection.status = 'accepted'
        connection.accepted_at = timezone.now()
        connection.save()
        
        # Update mentor profile mentee count
        profile, created = MentorProfile.objects.get_or_create(mentor=request.user)
        profile.current_mentee_count = request.user.mentor_connections.filter(status='accepted').count()
        profile.save()
        
        messages.success(request, f'You have accepted the mentorship request from {connection.mentee.get_full_name() or connection.mentee.username}.')
    else:
        messages.warning(request, 'This request has already been processed.')
    
    return redirect('mentorship:mentor_mentees')


@login_required
def reject_connection(request, connection_id):
    """Reject a mentorship connection request"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can reject requests.')
        return redirect('dashboard:index')
    
    connection = get_object_or_404(MentorshipConnection, id=connection_id, mentor=request.user)
    
    if connection.status == 'pending':
        reason = request.POST.get('reason', '').strip()
        connection.status = 'rejected'
        if reason:
            connection.notes = reason
        connection.save()
        messages.info(request, 'Mentorship request rejected.')
    else:
        messages.warning(request, 'This request has already been processed.')
    
    return redirect('mentorship:mentor_mentees')


@login_required
def mentor_sessions(request):
    """Mentor's sessions list"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can access this page.')
        return redirect('dashboard:index')
    
    # Get all connections for this mentor
    connections = MentorshipConnection.objects.filter(mentor=request.user, status='accepted')
    sessions = MentorshipSession.objects.filter(connection__in=connections).select_related('connection__mentee').order_by('scheduled_date')
    
    upcoming_sessions = sessions.filter(status='scheduled', scheduled_date__gte=timezone.now())
    past_sessions = sessions.filter(status='completed') | sessions.filter(scheduled_date__lt=timezone.now()).exclude(status='scheduled')
    
    context = {
        'page_title': 'My Sessions',
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
    }
    return render(request, 'mentorship/mentor_sessions.html', context)


@login_required
def session_create(request):
    """Create a new session"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can create sessions.')
        return redirect('dashboard:index')
    
    connections = MentorshipConnection.objects.filter(mentor=request.user, status='accepted').select_related('mentee')
    
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            # Get connection from form
            connection_id = request.POST.get('connection')
            connection = get_object_or_404(MentorshipConnection, id=connection_id, mentor=request.user)
            session.connection = connection
            session.save()
            messages.success(request, 'Session created successfully!')
            return redirect('mentorship:session_detail', session_id=session.id)
    else:
        form = SessionForm()
    
    context = {
        'page_title': 'Create New Session',
        'form': form,
        'connections': connections,
    }
    return render(request, 'mentorship/session_form.html', context)


@login_required
def session_detail(request, session_id):
    """View session details"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can access this page.')
        return redirect('dashboard:index')
    
    session = get_object_or_404(MentorshipSession, id=session_id, connection__mentor=request.user)
    
    context = {
        'page_title': session.title,
        'session': session,
    }
    return render(request, 'mentorship/session_detail.html', context)


@login_required
def session_edit(request, session_id):
    """Edit a session"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can edit sessions.')
        return redirect('dashboard:index')
    
    session = get_object_or_404(MentorshipSession, id=session_id, connection__mentor=request.user)
    connections = MentorshipConnection.objects.filter(mentor=request.user, status='accepted')
    
    if request.method == 'POST':
        form = SessionForm(request.POST, instance=session)
        if form.is_valid():
            # Connection is handled via hidden field in template, so we just save
            form.save()
            messages.success(request, 'Session updated successfully!')
            return redirect('mentorship:session_detail', session_id=session.id)
    else:
        form = SessionForm(instance=session)
    
    context = {
        'page_title': f'Edit: {session.title}',
        'form': form,
        'session': session,
        'connections': connections,
    }
    return render(request, 'mentorship/session_form.html', context)


@login_required
def session_complete(request, session_id):
    """Mark session as completed"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can complete sessions.')
        return redirect('dashboard:index')
    
    session = get_object_or_404(MentorshipSession, id=session_id, connection__mentor=request.user)
    session.status = 'completed'
    session.save()
    messages.success(request, 'Session marked as completed!')
    return redirect('mentorship:session_detail', session_id=session.id)


@login_required
def mentor_resources(request):
    """Mentor's resources list"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can access this page.')
        return redirect('dashboard:index')
    
    resources = MentorResource.objects.filter(mentor=request.user).prefetch_related('connections').order_by('-created_at')
    
    context = {
        'page_title': 'My Resources',
        'resources': resources,
    }
    return render(request, 'mentorship/mentor_resources.html', context)


@login_required
def resource_create(request):
    """Create/upload a new resource"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can upload resources.')
        return redirect('dashboard:index')
    
    connections = MentorshipConnection.objects.filter(mentor=request.user, status='accepted').select_related('mentee')
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, mentor=request.user)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.mentor = request.user
            resource.save()
            form.save_m2m()  # Save many-to-many connections
            messages.success(request, 'Resource uploaded successfully!')
            return redirect('mentorship:mentor_resources')
    else:
        form = ResourceForm(mentor=request.user)
    
    context = {
        'page_title': 'Upload New Resource',
        'form': form,
        'connections': connections,
    }
    return render(request, 'mentorship/resource_form.html', context)


@login_required
def resource_edit(request, resource_id):
    """Edit a resource"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can edit resources.')
        return redirect('dashboard:index')
    
    resource = get_object_or_404(MentorResource, id=resource_id, mentor=request.user)
    connections = MentorshipConnection.objects.filter(mentor=request.user, status='accepted').select_related('mentee')
    
    if request.method == 'POST':
        form = ResourceForm(request.POST, request.FILES, instance=resource, mentor=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully!')
            return redirect('mentorship:mentor_resources')
    else:
        form = ResourceForm(instance=resource, mentor=request.user)
    
    context = {
        'page_title': f'Edit: {resource.title}',
        'form': form,
        'resource': resource,
        'connections': connections,
    }
    return render(request, 'mentorship/resource_form.html', context)


@login_required
def resource_delete(request, resource_id):
    """Delete a resource"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can delete resources.')
        return redirect('dashboard:index')
    
    resource = get_object_or_404(MentorResource, id=resource_id, mentor=request.user)
    
    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource deleted successfully!')
        return redirect('mentorship:mentor_resources')
    
    context = {
        'page_title': 'Delete Resource',
        'resource': resource,
    }
    return render(request, 'mentorship/resource_confirm_delete.html', context)


@login_required
def mentor_profile_edit(request):
    """Edit mentor professional profile"""
    if not request.user.is_mentor:
        messages.error(request, 'Only mentors can edit their professional profile.')
        return redirect('dashboard:index')
    
    profile, created = MentorProfile.objects.get_or_create(mentor=request.user)
    
    if request.method == 'POST':
        form = MentorProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('mentorship:mentor_profile_edit')
    else:
        form = MentorProfileForm(instance=profile)
    
    context = {
        'page_title': 'Edit Professional Profile',
        'form': form,
        'profile': profile,
    }
    return render(request, 'mentorship/mentor_profile_edit.html', context)
