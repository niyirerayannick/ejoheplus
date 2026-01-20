from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import Count
from django.forms import HiddenInput
from .models import StudentCV, Message, Notification, Article, Event
from .forms import (
    CVForm,
    MessageForm,
    ArticleForm,
    EventForm,
    CourseCreateForm,
    OpportunityCreateForm,
    StudentCreateForm,
    AdminUserCreateForm,
    AdminUserForm,
    AdminMentorCreateForm,
    AdminArticleForm,
    AdminCourseForm,
    AdminOpportunityForm,
    CareerForm,
    AdminCourseMaterialForm,
    AdminEnrollmentForm,
    AdminCertificateForm,
    AdminMentorAssignmentForm,
)
from opportunities.models import Application, Opportunity
from accounts.models import User
from mentorship.models import MentorshipConnection
from training.models import Enrollment, Course, CourseMaterial, Certificate
from careers.models import Career
from careers.models import CareerDiscoveryResponse


@login_required
def index(request):
    """Main dashboard router - redirects based on user role"""
    user = request.user
    
    if user.is_administrator:
        return redirect('dashboard:admin_dashboard')
    elif user.is_mentor:
        return redirect('dashboard:mentor_dashboard')
    elif user.is_partner:
        return redirect('dashboard:partner_dashboard')
    else:
        return redirect('dashboard:student_dashboard')


@login_required
def student_dashboard(request):
    """Student Dashboard"""
    if not request.user.is_student:
        return redirect('dashboard:index')
    
    # Get real stats
    applications = Application.objects.filter(student=request.user)
    approved_connections = MentorshipConnection.objects.filter(mentee=request.user, status='accepted').select_related('mentor')
    pending_connections = MentorshipConnection.objects.filter(mentee=request.user, status='pending').select_related('mentor')
    trainings = Enrollment.objects.filter(student=request.user)
    unread_messages = Message.objects.filter(recipient=request.user, is_read=False)
    
    context = {
        'page_title': 'Student Dashboard',
        'stats': {
            'applications': applications.count(),
            'mentors': approved_connections.count(),
            'courses': trainings.count(),
            'messages': unread_messages.count(),
        },
        'recent_applications': applications[:5],
        'recent_mentors': approved_connections[:3],
        'pending_mentor_requests': pending_connections[:3],
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@login_required
def mentor_dashboard(request):
    """Mentor Dashboard"""
    if not request.user.is_mentor:
        return redirect('dashboard:index')
    
    from mentorship.models import MentorshipConnection, MentorshipSession
    from django.utils import timezone
    from training.models import Course
    
    # Get real stats
    connections = MentorshipConnection.objects.filter(mentor=request.user, status='accepted')
    upcoming_sessions = MentorshipSession.objects.filter(
        connection__in=connections,
        status='scheduled',
        scheduled_date__gte=timezone.now()
    )
    trainings = Course.objects.filter(created_by=request.user).order_by('-created_at')
    events = Event.objects.filter(creator=request.user).order_by('-start_date')
    unread_messages = Message.objects.filter(recipient=request.user, is_read=False)
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)
    
    context = {
        'page_title': 'Mentor Dashboard',
        'stats': {
            'mentees': connections.count(),
            'courses': trainings.count(),
            'events': events.count(),
            'messages': unread_messages.count(),
            'notifications': unread_notifications.count(),
        },
        'upcoming_sessions': upcoming_sessions.select_related('connection__mentee')[:5],
        'recent_trainings': trainings[:4],
        'recent_events': events[:4],
        'recent_mentees': connections.select_related('mentee')[:3],
    }
    return render(request, 'dashboard/mentor_dashboard.html', context)


@login_required
def partner_dashboard(request):
    """Partner Dashboard"""
    if not request.user.is_partner:
        return redirect('dashboard:index')
    
    opportunities_qs = Opportunity.objects.filter(created_by=request.user)
    opportunities = opportunities_qs.count()
    trainings = Course.objects.filter(created_by=request.user).count()
    events = Event.objects.filter(creator=request.user).count()
    applications = Application.objects.filter(opportunity__in=opportunities_qs)

    context = {
        'page_title': 'Partner Dashboard',
        'stats': {
            'opportunities': opportunities,
            'applications': applications.count(),
            'events': events,
            'courses': trainings,
        },
        'recent_applications': applications.select_related('student', 'opportunity')[:5],
    }
    return render(request, 'dashboard/partner_dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Admin Dashboard"""
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    pending_mentors = User.objects.filter(role='mentor', is_mentor_approved=False, is_active=True).order_by('-date_joined')[:5]

    context = {
        'page_title': 'Admin Dashboard',
        'stats': {
            'users': User.objects.count(),
            'mentor_approvals': User.objects.filter(role='mentor', is_mentor_approved=False, is_active=True).count(),
            'opportunities': Opportunity.objects.count(),
            'courses': Course.objects.count(),
            'career_assessments': CareerDiscoveryResponse.objects.count(),
        },
        'pending_mentors': pending_mentors,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def admin_users(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    users = User.objects.order_by('-date_joined')
    context = {
        'page_title': 'Users',
        'users': users,
    }
    return render(request, 'dashboard/admin_users.html', context)


@login_required
def admin_user_create(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('dashboard:admin_users')
    else:
        form = AdminUserCreateForm()

    context = {
        'page_title': 'Add User',
        'form': form,
    }
    return render(request, 'dashboard/admin_user_form.html', context)


@login_required
def admin_user_edit(request, user_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    user_obj = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = AdminUserForm(request.POST, request.FILES, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('dashboard:admin_users')
    else:
        form = AdminUserForm(instance=user_obj)

    context = {
        'page_title': 'Edit User',
        'form': form,
    }
    return render(request, 'dashboard/admin_user_form.html', context)


@login_required
def admin_user_delete(request, user_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_users')

    user_obj = get_object_or_404(User, id=user_id)
    user_obj.delete()
    messages.info(request, 'User deleted.')
    return redirect('dashboard:admin_users')


@login_required
def admin_mentors(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    mentors = User.objects.filter(role='mentor').order_by('-date_joined')
    context = {
        'page_title': 'Mentors',
        'mentors': mentors,
    }
    return render(request, 'dashboard/admin_mentors.html', context)


@login_required
def admin_assign_mentor(request, mentor_id=None):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    form = AdminMentorAssignmentForm(request.POST or None)
    if mentor_id:
        form.fields['mentor'].initial = get_object_or_404(User, id=mentor_id, role='mentor')

    if request.method == 'POST' and form.is_valid():
        mentor = form.cleaned_data['mentor']
        mentee = form.cleaned_data['mentee']
        notes = form.cleaned_data['notes']
        connection, created = MentorshipConnection.objects.get_or_create(
            mentor=mentor,
            mentee=mentee,
            defaults={'status': 'accepted', 'accepted_at': timezone.now(), 'notes': notes}
        )
        if not created:
            connection.status = 'accepted'
            connection.accepted_at = timezone.now()
            connection.notes = notes
            connection.save()
        messages.success(request, 'Student assigned to mentor successfully.')
        return redirect('dashboard:admin_mentors')

    context = {
        'page_title': 'Assign Mentor',
        'form': form,
    }
    return render(request, 'dashboard/admin_mentor_assign.html', context)


@login_required
def admin_mentor_create(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = AdminMentorCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mentor created successfully.')
            return redirect('dashboard:admin_mentors')
    else:
        form = AdminMentorCreateForm()

    context = {
        'page_title': 'Add Mentor',
        'form': form,
    }
    return render(request, 'dashboard/admin_user_form.html', context)


@login_required
def admin_mentor_edit(request, mentor_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    mentor = get_object_or_404(User, id=mentor_id, role='mentor')
    if request.method == 'POST':
        form = AdminUserForm(request.POST, request.FILES, instance=mentor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mentor updated successfully.')
            return redirect('dashboard:admin_mentors')
    else:
        form = AdminUserForm(instance=mentor)

    context = {
        'page_title': 'Edit Mentor',
        'form': form,
    }
    return render(request, 'dashboard/admin_user_form.html', context)


@login_required
def admin_mentor_delete(request, mentor_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_mentors')

    mentor = get_object_or_404(User, id=mentor_id, role='mentor')
    mentor.delete()
    messages.info(request, 'Mentor deleted.')
    return redirect('dashboard:admin_mentors')


@login_required
def admin_mentor_approvals(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    pending = User.objects.filter(role='mentor', is_mentor_approved=False, is_active=True).order_by('-date_joined')
    context = {
        'page_title': 'Mentor Approvals',
        'pending_mentors': pending,
    }
    return render(request, 'dashboard/admin_mentor_approvals.html', context)


@login_required
def admin_mentor_approve(request, mentor_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_mentor_approvals')

    mentor = get_object_or_404(User, id=mentor_id, role='mentor')
    mentor.is_mentor_approved = True
    mentor.is_active = True
    mentor.save()
    messages.success(request, f'{mentor.get_full_name() or mentor.username} approved successfully.')
    return redirect('dashboard:admin_mentor_approvals')


@login_required
def admin_mentor_reject(request, mentor_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_mentor_approvals')

    mentor = get_object_or_404(User, id=mentor_id, role='mentor')
    mentor.is_mentor_approved = False
    mentor.is_active = False
    mentor.save()
    messages.info(request, f'{mentor.get_full_name() or mentor.username} rejected.')
    return redirect('dashboard:admin_mentor_approvals')


@login_required
def admin_publications(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    return redirect('dashboard:admin_articles')


@login_required
def admin_articles(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    articles = Article.objects.order_by('-created_at')
    context = {
        'page_title': 'Articles',
        'articles': articles,
    }
    return render(request, 'dashboard/admin_articles.html', context)


@login_required
def admin_article_create(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = AdminArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            base_slug = slugify(article.title)[:60] or f"article-{request.user.id}"
            article.slug = _generate_unique_slug(Article, base_slug)
            if article.status == 'published' and not article.published_at:
                article.published_at = timezone.now()
            article.save()
            messages.success(request, 'Article created successfully.')
            return redirect('dashboard:admin_articles')
    else:
        form = AdminArticleForm()

    context = {
        'page_title': 'Add Article',
        'form': form,
    }
    return render(request, 'dashboard/admin_article_form.html', context)


@login_required
def admin_article_edit(request, article_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    article = get_object_or_404(Article, id=article_id)
    if request.method == 'POST':
        form = AdminArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            if not article.slug:
                base_slug = slugify(article.title)[:60] or f"article-{request.user.id}"
                article.slug = _generate_unique_slug(Article, base_slug)
            if article.status == 'published' and not article.published_at:
                article.published_at = timezone.now()
            article.save()
            messages.success(request, 'Article updated successfully.')
            return redirect('dashboard:admin_articles')
    else:
        form = AdminArticleForm(instance=article)

    context = {
        'page_title': 'Edit Article',
        'form': form,
    }
    return render(request, 'dashboard/admin_article_form.html', context)


@login_required
def admin_article_delete(request, article_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_articles')

    article = get_object_or_404(Article, id=article_id)
    article.delete()
    messages.info(request, 'Article deleted.')
    return redirect('dashboard:admin_articles')


@login_required
def admin_careers(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    careers = Career.objects.order_by('title')
    context = {
        'page_title': 'Careers',
        'careers': careers,
    }
    return render(request, 'dashboard/admin_careers.html', context)


@login_required
def admin_career_create(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = CareerForm(request.POST, request.FILES)
        if form.is_valid():
            career = form.save(commit=False)
            if not career.slug:
                base_slug = slugify(career.title)[:60] or f"career-{request.user.id}"
                career.slug = _generate_unique_slug(Career, base_slug)
            career.save()
            messages.success(request, 'Career created successfully.')
            return redirect('dashboard:admin_careers')
    else:
        form = CareerForm()

    context = {
        'page_title': 'Add Career',
        'form': form,
    }
    return render(request, 'dashboard/admin_career_form.html', context)


@login_required
def admin_career_edit(request, career_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    career = get_object_or_404(Career, id=career_id)
    if request.method == 'POST':
        form = CareerForm(request.POST, request.FILES, instance=career)
        if form.is_valid():
            career = form.save(commit=False)
            if not career.slug:
                base_slug = slugify(career.title)[:60] or f"career-{request.user.id}"
                career.slug = _generate_unique_slug(Career, base_slug)
            career.save()
            messages.success(request, 'Career updated successfully.')
            return redirect('dashboard:admin_careers')
    else:
        form = CareerForm(instance=career)

    context = {
        'page_title': 'Edit Career',
        'form': form,
    }
    return render(request, 'dashboard/admin_career_form.html', context)


@login_required
def admin_career_delete(request, career_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_careers')

    career = get_object_or_404(Career, id=career_id)
    career.delete()
    messages.info(request, 'Career deleted.')
    return redirect('dashboard:admin_careers')


@login_required
def admin_opportunities(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    opportunities = Opportunity.objects.order_by('-created_at')
    context = {
        'page_title': 'Opportunities',
        'opportunities': opportunities,
    }
    return render(request, 'dashboard/admin_opportunities.html', context)


@login_required
def admin_opportunity_create(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = AdminOpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            if not opportunity.slug:
                base_slug = slugify(opportunity.title)[:60] or f"opportunity-{request.user.id}"
                opportunity.slug = _generate_unique_slug(Opportunity, base_slug)
            opportunity.save()
            messages.success(request, 'Opportunity created successfully.')
            return redirect('dashboard:admin_opportunities')
    else:
        form = AdminOpportunityForm()

    context = {
        'page_title': 'Add Opportunity',
        'form': form,
    }
    return render(request, 'dashboard/admin_opportunity_form.html', context)


@login_required
def admin_opportunity_edit(request, opportunity_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    if request.method == 'POST':
        form = AdminOpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            opportunity = form.save(commit=False)
            if not opportunity.slug:
                base_slug = slugify(opportunity.title)[:60] or f"opportunity-{request.user.id}"
                opportunity.slug = _generate_unique_slug(Opportunity, base_slug)
            opportunity.save()
            messages.success(request, 'Opportunity updated successfully.')
            return redirect('dashboard:admin_opportunities')
    else:
        form = AdminOpportunityForm(instance=opportunity)

    context = {
        'page_title': 'Edit Opportunity',
        'form': form,
    }
    return render(request, 'dashboard/admin_opportunity_form.html', context)


@login_required
def admin_opportunity_delete(request, opportunity_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_opportunities')

    opportunity = get_object_or_404(Opportunity, id=opportunity_id)
    opportunity.delete()
    messages.info(request, 'Opportunity deleted.')
    return redirect('dashboard:admin_opportunities')


@login_required
def admin_trainings(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    trainings = Course.objects.order_by('-created_at')
    context = {
        'page_title': 'Courses',
        'trainings': trainings,
    }
    return render(request, 'dashboard/admin_trainings.html', context)


@login_required
def admin_training_create(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = AdminCourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            if not course.slug:
                base_slug = slugify(course.title)[:60] or f"course-{request.user.id}"
                course.slug = _generate_unique_slug(Course, base_slug)
            course.save()
            messages.success(request, 'Course created successfully.')
            return redirect('dashboard:admin_courses')
    else:
        form = AdminCourseForm()

    context = {
        'page_title': 'Add Course',
        'form': form,
    }
    return render(request, 'dashboard/admin_training_form.html', context)


@login_required
def admin_training_edit(request, training_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    training = get_object_or_404(Course, id=training_id)
    if request.method == 'POST':
        form = AdminCourseForm(request.POST, request.FILES, instance=training)
        if form.is_valid():
            course = form.save(commit=False)
            if not course.slug:
                base_slug = slugify(course.title)[:60] or f"course-{request.user.id}"
                course.slug = _generate_unique_slug(Course, base_slug)
            course.save()
            messages.success(request, 'Course updated successfully.')
            return redirect('dashboard:admin_courses')
    else:
        form = AdminCourseForm(instance=training)

    context = {
        'page_title': 'Edit Course',
        'form': form,
    }
    return render(request, 'dashboard/admin_training_form.html', context)


@login_required
def admin_training_delete(request, training_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_courses')

    training = get_object_or_404(Course, id=training_id)
    training.delete()
    messages.info(request, 'Course deleted.')
    return redirect('dashboard:admin_courses')


@login_required
def admin_materials(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    materials = CourseMaterial.objects.select_related('course').order_by('course__title', 'order')
    context = {
        'page_title': 'Course Materials',
        'materials': materials,
    }
    return render(request, 'dashboard/admin_materials.html', context)


@login_required
def admin_material_create(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = AdminCourseMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course material created successfully.')
            return redirect('dashboard:admin_materials')
    else:
        form = AdminCourseMaterialForm()

    context = {
        'page_title': 'Add Course Material',
        'form': form,
    }
    return render(request, 'dashboard/admin_material_form.html', context)


@login_required
def admin_material_edit(request, material_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    material = get_object_or_404(CourseMaterial, id=material_id)
    if request.method == 'POST':
        form = AdminCourseMaterialForm(request.POST, request.FILES, instance=material)
        if form.is_valid():
            form.save()
            messages.success(request, 'Course material updated successfully.')
            return redirect('dashboard:admin_materials')
    else:
        form = AdminCourseMaterialForm(instance=material)

    context = {
        'page_title': 'Edit Course Material',
        'form': form,
    }
    return render(request, 'dashboard/admin_material_form.html', context)


@login_required
def admin_material_delete(request, material_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_materials')

    material = get_object_or_404(CourseMaterial, id=material_id)
    material.delete()
    messages.info(request, 'Course material deleted.')
    return redirect('dashboard:admin_materials')


@login_required
def admin_enrollments(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    enrollments = Enrollment.objects.select_related('course', 'student').order_by('-enrolled_at')
    context = {
        'page_title': 'Enrollments',
        'enrollments': enrollments,
    }
    return render(request, 'dashboard/admin_enrollments.html', context)


@login_required
def admin_enrollment_create(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = AdminEnrollmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enrollment created successfully.')
            return redirect('dashboard:admin_enrollments')
    else:
        form = AdminEnrollmentForm()

    context = {
        'page_title': 'Add Enrollment',
        'form': form,
    }
    return render(request, 'dashboard/admin_enrollment_form.html', context)


@login_required
def admin_enrollment_edit(request, enrollment_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    if request.method == 'POST':
        form = AdminEnrollmentForm(request.POST, instance=enrollment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enrollment updated successfully.')
            return redirect('dashboard:admin_enrollments')
    else:
        form = AdminEnrollmentForm(instance=enrollment)

    context = {
        'page_title': 'Edit Enrollment',
        'form': form,
    }
    return render(request, 'dashboard/admin_enrollment_form.html', context)


@login_required
def admin_enrollment_delete(request, enrollment_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_enrollments')

    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    enrollment.delete()
    messages.info(request, 'Enrollment deleted.')
    return redirect('dashboard:admin_enrollments')


@login_required
def admin_certificates(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    certificates = Certificate.objects.select_related('enrollment__course', 'enrollment__student').order_by('-issued_at')
    context = {
        'page_title': 'Certificates',
        'certificates': certificates,
    }
    return render(request, 'dashboard/admin_certificates.html', context)


@login_required
def admin_certificate_create(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = AdminCertificateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Certificate created successfully.')
            return redirect('dashboard:admin_certificates')
    else:
        form = AdminCertificateForm()

    context = {
        'page_title': 'Add Certificate',
        'form': form,
    }
    return render(request, 'dashboard/admin_certificate_form.html', context)


@login_required
def admin_certificate_edit(request, certificate_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    certificate = get_object_or_404(Certificate, id=certificate_id)
    if request.method == 'POST':
        form = AdminCertificateForm(request.POST, instance=certificate)
        if form.is_valid():
            form.save()
            messages.success(request, 'Certificate updated successfully.')
            return redirect('dashboard:admin_certificates')
    else:
        form = AdminCertificateForm(instance=certificate)

    context = {
        'page_title': 'Edit Certificate',
        'form': form,
    }
    return render(request, 'dashboard/admin_certificate_form.html', context)


@login_required
def admin_certificate_delete(request, certificate_id):
    if not request.user.is_administrator:
        return redirect('dashboard:index')
    if request.method != 'POST':
        return redirect('dashboard:admin_certificates')

    certificate = get_object_or_404(Certificate, id=certificate_id)
    certificate.delete()
    messages.info(request, 'Certificate deleted.')
    return redirect('dashboard:admin_certificates')


@login_required
def admin_reports(request):
    if not request.user.is_administrator:
        return redirect('dashboard:index')

    context = {
        'page_title': 'Reports',
        'stats': {
            'applications': Application.objects.count(),
            'mentorship_requests': MentorshipConnection.objects.filter(status='pending').count(),
            'active_courses': Course.objects.filter(is_active=True).count(),
            'active_opportunities': Opportunity.objects.filter(is_active=True).count(),
        },
    }
    return render(request, 'dashboard/admin_reports.html', context)


def _generate_unique_slug(model, base_slug):
    slug = base_slug
    counter = 1
    while model.objects.filter(slug=slug).exists():
        counter += 1
        slug = f"{base_slug}-{counter}"
    return slug


def _dashboard_base_template(user):
    if user.is_student:
        return 'dashboard/base_student_dashboard.html'
    if user.is_mentor:
        return 'dashboard/base_mentor_dashboard.html'
    if user.is_partner:
        return 'dashboard/base_partner_dashboard.html'
    if user.is_administrator:
        return 'dashboard/base_admin_dashboard.html'
    return 'dashboard/base_student_dashboard.html'


@login_required
def profile(request):
    """User profile page"""
    context = {
        'page_title': 'My Profile',
    }
    
    # Determine which template to use based on user role
    if request.user.is_student:
        template = 'dashboard/profile_student.html'
    elif request.user.is_mentor:
        template = 'dashboard/profile_mentor.html'
    elif request.user.is_partner:
        template = 'dashboard/profile_partner.html'
    elif request.user.is_administrator:
        template = 'dashboard/profile_admin.html'
    else:
        template = 'dashboard/profile.html'
    
    return render(request, template, context)


# CV Builder Views
@login_required
def cv_builder(request):
    """CV Builder for students"""
    if not request.user.is_student:
        messages.error(request, 'Only students can access the CV builder.')
        return redirect('dashboard:index')
    
    cv, created = StudentCV.objects.get_or_create(student=request.user)
    
    if request.method == 'POST':
        form = CVForm(request.POST, instance=cv)
        if form.is_valid():
            form.save()
            messages.success(request, 'CV updated successfully!')
            return redirect('dashboard:cv_builder')
    else:
        form = CVForm(instance=cv)
    
    context = {
        'page_title': 'My CV Builder',
        'form': form,
        'cv': cv,
    }
    return render(request, 'dashboard/cv_builder.html', context)


@login_required
def cv_preview(request):
    """CV Preview for students"""
    if not request.user.is_student:
        messages.error(request, 'Only students can preview their CV.')
        return redirect('dashboard:index')
    
    cv = get_object_or_404(StudentCV, student=request.user)
    
    context = {
        'page_title': 'CV Preview',
        'cv': cv,
    }
    return render(request, 'dashboard/cv_preview.html', context)


# Articles
@login_required
def articles_list(request):
    if not (request.user.is_student or request.user.is_mentor or request.user.is_partner):
        messages.error(request, 'You do not have access to articles.')
        return redirect('dashboard:index')

    articles = Article.objects.filter(author=request.user).order_by('-created_at')
    context = {
        'page_title': 'My Articles',
        'articles': articles,
        'base_template': _dashboard_base_template(request.user),
    }
    return render(request, 'dashboard/articles_list.html', context)


@login_required
def article_create(request):
    if not (request.user.is_student or request.user.is_mentor or request.user.is_partner):
        messages.error(request, 'You do not have access to create articles.')
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            base_slug = slugify(article.title)[:60] or f"article-{request.user.id}"
            article.slug = _generate_unique_slug(Article, base_slug)
            if article.status == 'published' and not article.published_at:
                article.published_at = timezone.now()
            article.save()
            messages.success(request, 'Article saved successfully.')
            return redirect('dashboard:articles_list')
    else:
        form = ArticleForm()

    context = {
        'page_title': 'Create Article',
        'form': form,
        'base_template': _dashboard_base_template(request.user),
    }
    return render(request, 'dashboard/article_form.html', context)


# Events
@login_required
def events_list(request):
    if not (request.user.is_mentor or request.user.is_partner):
        messages.error(request, 'You do not have access to events.')
        return redirect('dashboard:index')

    events = Event.objects.filter(creator=request.user).order_by('-start_date')
    context = {
        'page_title': 'My Events',
        'events': events,
        'base_template': _dashboard_base_template(request.user),
    }
    return render(request, 'dashboard/events_list.html', context)


@login_required
def event_create(request):
    if not (request.user.is_mentor or request.user.is_partner):
        messages.error(request, 'You do not have access to create events.')
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = request.user
            base_slug = slugify(event.title)[:60] or f"event-{request.user.id}"
            event.slug = _generate_unique_slug(Event, base_slug)
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('dashboard:events_list')
    else:
        form = EventForm()

    context = {
        'page_title': 'Create Event',
        'form': form,
        'base_template': _dashboard_base_template(request.user),
    }
    return render(request, 'dashboard/event_form.html', context)


# Courses (Mentor/Partner)
@login_required
def courses_list(request):
    if request.user.is_administrator:
        return redirect('dashboard:admin_courses')
    if not (request.user.is_mentor or request.user.is_partner):
        messages.error(request, 'You do not have access to courses.')
        return redirect('dashboard:index')

    courses = (
        Course.objects.filter(created_by=request.user)
        .annotate(
            chapter_count=Count('chapters', distinct=True),
            quiz_count=Count('quizzes', distinct=True),
            enrollment_count=Count('enrollments', distinct=True),
            materials_count=Count('materials', distinct=True),
        )
        .order_by('-created_at')
    )
    total_courses = courses.count()
    active_courses = courses.filter(is_active=True).count()
    draft_courses = total_courses - active_courses
    context = {
        'page_title': 'My Courses',
        'courses': courses,
        'stats': {
            'total': total_courses,
            'active': active_courses,
            'drafts': draft_courses,
        },
        'base_template': _dashboard_base_template(request.user),
    }
    return render(request, 'dashboard/courses_list.html', context)


@login_required
def course_manage(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if not (request.user.is_administrator or course.created_by == request.user or course.instructor == request.user):
        messages.error(request, 'You do not have permission to manage this course.')
        return redirect('dashboard:courses_list')

    base_template = _dashboard_base_template(request.user)
    materials = CourseMaterial.objects.filter(course=course).order_by('order', 'created_at')
    enrollments = Enrollment.objects.filter(course=course).select_related('student').order_by('-enrolled_at')
    certificates = Certificate.objects.filter(enrollment__course=course).select_related('enrollment__student')
    completed_count = enrollments.filter(is_completed=True).count()
    completion_rate = int((completed_count / enrollments.count()) * 100) if enrollments else 0

    edit_material = None
    edit_enrollment = None
    edit_certificate = None
    if request.GET.get('edit_material'):
        edit_material = get_object_or_404(CourseMaterial, id=request.GET.get('edit_material'), course=course)
    if request.GET.get('edit_enrollment'):
        edit_enrollment = get_object_or_404(Enrollment, id=request.GET.get('edit_enrollment'), course=course)
    if request.GET.get('edit_certificate'):
        edit_certificate = get_object_or_404(Certificate, id=request.GET.get('edit_certificate'), enrollment__course=course)

    course_form_class = AdminCourseForm if request.user.is_administrator else CourseCreateForm
    course_form = course_form_class(prefix='course', instance=course)
    material_form = AdminCourseMaterialForm(prefix='material', instance=edit_material)
    enrollment_form = AdminEnrollmentForm(prefix='enrollment', instance=edit_enrollment)
    certificate_form = AdminCertificateForm(prefix='certificate', instance=edit_certificate)

    material_form.fields['course'].initial = course
    material_form.fields['course'].widget = HiddenInput()
    enrollment_form.fields['course'].initial = course
    enrollment_form.fields['course'].widget = HiddenInput()
    certificate_form.fields['enrollment'].queryset = enrollments

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_course':
            course_form = course_form_class(request.POST, request.FILES, prefix='course', instance=course)
            if course_form.is_valid():
                course_form.save()
                messages.success(request, 'Course details updated.')
                return redirect('dashboard:course_manage', course_id=course.id)
        elif action == 'set_status':
            status = request.POST.get('status')
            if status == 'publish':
                course.is_active = True
                course.save(update_fields=['is_active'])
                messages.success(request, 'Course published.')
            elif status == 'archive':
                course.is_active = False
                course.save(update_fields=['is_active'])
                messages.info(request, 'Course archived.')
            return redirect('dashboard:course_manage', course_id=course.id)
        elif action == 'save_material':
            material_id = request.POST.get('material_id')
            material_instance = edit_material if material_id else None
            if material_id:
                material_instance = get_object_or_404(CourseMaterial, id=material_id, course=course)
            material_form = AdminCourseMaterialForm(request.POST, request.FILES, prefix='material', instance=material_instance)
            material_form.fields['course'].initial = course
            material_form.fields['course'].widget = HiddenInput()
            if material_form.is_valid():
                material_form.save()
                messages.success(request, 'Course material saved.')
                return redirect('dashboard:course_manage', course_id=course.id)
        elif action == 'delete_material':
            material_id = request.POST.get('material_id')
            material = get_object_or_404(CourseMaterial, id=material_id, course=course)
            material.delete()
            messages.info(request, 'Course material deleted.')
            return redirect('dashboard:course_manage', course_id=course.id)
        elif action == 'reorder_materials':
            order_list = request.POST.get('material_order', '')
            ids = [int(item) for item in order_list.split(',') if item.isdigit()]
            for index, material_id in enumerate(ids, start=1):
                CourseMaterial.objects.filter(id=material_id, course=course).update(order=index)
            messages.success(request, 'Material order updated.')
            return redirect('dashboard:course_manage', course_id=course.id)
        elif action == 'save_enrollment':
            enrollment_id = request.POST.get('enrollment_id')
            enrollment_instance = edit_enrollment if enrollment_id else None
            if enrollment_id:
                enrollment_instance = get_object_or_404(Enrollment, id=enrollment_id, course=course)
            enrollment_form = AdminEnrollmentForm(request.POST, prefix='enrollment', instance=enrollment_instance)
            enrollment_form.fields['course'].initial = course
            enrollment_form.fields['course'].widget = HiddenInput()
            if enrollment_form.is_valid():
                enrollment_form.save()
                messages.success(request, 'Enrollment saved.')
                return redirect('dashboard:course_manage', course_id=course.id)
        elif action == 'delete_enrollment':
            enrollment_id = request.POST.get('enrollment_id')
            enrollment = get_object_or_404(Enrollment, id=enrollment_id, course=course)
            enrollment.delete()
            messages.info(request, 'Enrollment deleted.')
            return redirect('dashboard:course_manage', course_id=course.id)
        elif action == 'save_certificate':
            certificate_id = request.POST.get('certificate_id')
            certificate_instance = edit_certificate if certificate_id else None
            if certificate_id:
                certificate_instance = get_object_or_404(Certificate, id=certificate_id, enrollment__course=course)
            certificate_form = AdminCertificateForm(request.POST, prefix='certificate', instance=certificate_instance)
            certificate_form.fields['enrollment'].queryset = enrollments
            if certificate_form.is_valid():
                certificate_form.save()
                messages.success(request, 'Certificate saved.')
                return redirect('dashboard:course_manage', course_id=course.id)
        elif action == 'delete_certificate':
            certificate_id = request.POST.get('certificate_id')
            certificate = get_object_or_404(Certificate, id=certificate_id, enrollment__course=course)
            certificate.delete()
            messages.info(request, 'Certificate deleted.')
            return redirect('dashboard:course_manage', course_id=course.id)

    context = {
        'page_title': f'Manage Course: {course.title}',
        'course': course,
        'materials': materials,
        'enrollments': enrollments,
        'certificates': certificates,
        'completion_rate': completion_rate,
        'course_form': course_form,
        'material_form': material_form,
        'enrollment_form': enrollment_form,
        'certificate_form': certificate_form,
        'edit_material': edit_material,
        'edit_enrollment': edit_enrollment,
        'edit_certificate': edit_certificate,
        'base_template': base_template,
    }
    return render(request, 'dashboard/course_manage.html', context)


# Courses (Mentor/Partner)
@login_required
def training_create(request):
    if not (request.user.is_mentor or request.user.is_partner):
        messages.error(request, 'You do not have access to create courses.')
        return redirect('dashboard:index')
    return redirect('courses:course_create')


@login_required
def course_create(request):
    if not (request.user.is_mentor or request.user.is_partner):
        messages.error(request, 'You do not have access to create courses.')
        return redirect('dashboard:index')
    return redirect('courses:course_create')


# Opportunities (Mentor/Partner)
@login_required
def opportunity_create(request):
    if not (request.user.is_mentor or request.user.is_partner):
        messages.error(request, 'You do not have access to post opportunities.')
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = OpportunityCreateForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            if hasattr(opportunity, 'created_by'):
                opportunity.created_by = request.user
            if not opportunity.slug:
                base_slug = slugify(opportunity.title)[:60] or f"opportunity-{request.user.id}"
                opportunity.slug = _generate_unique_slug(Opportunity, base_slug)
            opportunity.save()
            messages.success(request, 'Opportunity posted successfully.')
            return redirect('dashboard:index')
        messages.error(request, 'Please fix the errors below and try again.')
    else:
        form = OpportunityCreateForm()

    context = {
        'page_title': 'Post Opportunity',
        'form': form,
        'base_template': _dashboard_base_template(request.user),
    }
    return render(request, 'dashboard/opportunity_form.html', context)


# Partner students management
@login_required
def partner_students(request):
    if not request.user.is_partner:
        messages.error(request, 'Only partners can manage students.')
        return redirect('dashboard:index')

    students = User.objects.filter(role='student').order_by('-date_joined')
    context = {
        'page_title': 'Manage Students',
        'students': students,
        'base_template': _dashboard_base_template(request.user),
    }
    return render(request, 'dashboard/partner_students.html', context)


@login_required
def partner_student_create(request):
    if not request.user.is_partner:
        messages.error(request, 'Only partners can add students.')
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = StudentCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student account created successfully.')
            return redirect('dashboard:partner_students')
    else:
        form = StudentCreateForm()

    context = {
        'page_title': 'Add Student',
        'form': form,
        'base_template': _dashboard_base_template(request.user),
    }
    return render(request, 'dashboard/partner_student_form.html', context)


# Messages Views
@login_required
def messages_list(request):
    """WhatsApp-style chat conversations list"""
    from django.db.models import Q, Max
    from accounts.models import User
    
    # Get all unique users you've conversed with
    conversations_query = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).values('sender', 'recipient').annotate(
        last_message_time=Max('created_at')
    ).order_by('-last_message_time')
    
    conversations = []
    seen_users = set()
    
    for conv in conversations_query:
        # Get the other user in the conversation
        if conv['sender'] == request.user.id:
            other_user_id = conv['recipient']
        else:
            other_user_id = conv['sender']
        
        # Avoid duplicates
        if other_user_id not in seen_users:
            seen_users.add(other_user_id)
            try:
                other_user = User.objects.get(id=other_user_id)
                # Get last message
                last_message = Message.objects.filter(
                    Q(sender=request.user, recipient=other_user) |
                    Q(sender=other_user, recipient=request.user)
                ).order_by('-created_at').first()
                
                # Count unread messages from this user
                unread = Message.objects.filter(
                    sender=other_user,
                    recipient=request.user,
                    is_read=False
                ).count()
                
                conversations.append({
                    'user': other_user,
                    'last_message': last_message,
                    'unread_count': unread,
                    'last_message_time': conv['last_message_time'],
                })
            except User.DoesNotExist:
                continue
    
    # Sort by last message time
    conversations.sort(key=lambda x: x['last_message_time'], reverse=True)
    
    unread_count = Message.objects.filter(recipient=request.user, is_read=False).count()
    
    # Choose template based on user role
    if request.user.is_mentor:
        template = 'dashboard/chat_conversations_mentor.html'
    else:
        template = 'dashboard/chat_conversations.html'
    
    context = {
        'page_title': 'Chats',
        'conversations': conversations,
        'unread_count': unread_count,
    }
    return render(request, template, context)


@login_required
def message_create(request):
    """Create a new message - redirect to chat if recipient selected"""
    recipient_id = request.GET.get('recipient') or request.GET.get('reply_to')
    
    if recipient_id:
        # If recipient is provided, redirect directly to chat
        try:
            from accounts.models import User
            recipient = User.objects.get(id=recipient_id)
            return redirect('dashboard:chat_detail', user_id=recipient.id)
        except User.DoesNotExist:
            pass
    
    # Otherwise, show form to select recipient
    if request.method == 'POST':
        form = MessageForm(request.POST, sender=request.user)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            
            # Create notification for recipient
            Notification.objects.create(
                user=message.recipient,
                notification_type='other',
                title=f'New message from {request.user.get_full_name() or request.user.username}',
                message=message.body[:100],
                related_url=f'/dashboard/chat/{request.user.id}/'
            )
            
            messages.success(request, 'Message sent successfully!')
            return redirect('dashboard:chat_detail', user_id=message.recipient.id)
    else:
        form = MessageForm(sender=request.user)
    
    # Choose template based on user role
    if request.user.is_mentor:
        template = 'dashboard/message_form_mentor.html'
    else:
        template = 'dashboard/message_form.html'
    
    context = {
        'page_title': 'New Chat',
        'form': form,
    }
    return render(request, template, context)


@login_required
def message_detail(request, message_id):
    """View message details - redirect to chat"""
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user is sender or recipient
    if message.recipient != request.user and message.sender != request.user:
        messages.error(request, 'You do not have permission to view this message.')
        return redirect('dashboard:messages_list')
    
    # Redirect to chat with the other user
    if message.sender == request.user:
        other_user_id = message.recipient.id
    else:
        other_user_id = message.sender.id
    
    return redirect('dashboard:chat_detail', user_id=other_user_id)


@login_required
def chat_detail(request, user_id):
    """WhatsApp-style chat conversation with a specific user"""
    from accounts.models import User
    from django.db.models import Q, Max
    
    other_user = get_object_or_404(User, id=user_id)
    
    # Get all messages in this conversation
    chat_messages_list = list(Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).select_related('sender', 'recipient').order_by('created_at'))
    
    # Add date separators to messages
    chat_messages = []
    prev_date = None
    for msg in chat_messages_list:
        msg_date = msg.created_at.date()
        if prev_date is None or prev_date != msg_date:
            chat_messages.append({
                'type': 'date_separator',
                'date': msg.created_at.date(),
            })
        chat_messages.append({
            'type': 'message',
            'message': msg,
        })
        prev_date = msg_date
    
    # Mark all unread messages from this user as read
    Message.objects.filter(
        sender=other_user,
        recipient=request.user,
        is_read=False
    ).update(is_read=True)
    
    # Handle sending new message
    if request.method == 'POST':
        body = request.POST.get('message_body', '').strip()
        if body:
            new_message = Message.objects.create(
                sender=request.user,
                recipient=other_user,
                subject=f'Chat with {other_user.get_full_name() or other_user.username}',
                body=body
            )
            
            # Create notification for recipient
            Notification.objects.create(
                user=other_user,
                notification_type='other',
                title=f'New message from {request.user.get_full_name() or request.user.username}',
                message=body[:100],
                related_url=f'/dashboard/chat/{request.user.id}/'
            )
            
            return redirect('dashboard:chat_detail', user_id=user_id)
    
    # Get conversations list for sidebar
    conversations_query = Message.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).values('sender', 'recipient').annotate(
        last_message_time=Max('created_at')
    ).order_by('-last_message_time')
    
    conversations = []
    seen_users = set()
    
    for conv in conversations_query:
        if conv['sender'] == request.user.id:
            other_user_id = conv['recipient']
        else:
            other_user_id = conv['sender']
        
        if other_user_id not in seen_users:
            seen_users.add(other_user_id)
            try:
                conv_user = User.objects.get(id=other_user_id)
                last_message = Message.objects.filter(
                    Q(sender=request.user, recipient=conv_user) |
                    Q(sender=conv_user, recipient=request.user)
                ).order_by('-created_at').first()
                
                unread = Message.objects.filter(
                    sender=conv_user,
                    recipient=request.user,
                    is_read=False
                ).count()
                
                conversations.append({
                    'user': conv_user,
                    'last_message': last_message,
                    'unread_count': unread,
                    'last_message_time': conv['last_message_time'],
                })
            except User.DoesNotExist:
                continue
    
    conversations.sort(key=lambda x: x['last_message_time'], reverse=True)
    
    # Choose template based on user role
    if request.user.is_mentor:
        template = 'dashboard/chat_detail_mentor.html'
    else:
        template = 'dashboard/chat_detail.html'
    
    context = {
        'page_title': f'Chat with {other_user.get_full_name() or other_user.username}',
        'other_user': other_user,
        'chat_messages': chat_messages,
        'conversations': conversations,
    }
    return render(request, template, context)


@login_required
def message_delete(request, message_id):
    """Delete a message"""
    message = get_object_or_404(Message, id=message_id)
    
    # Only sender or recipient can delete
    if message.sender != request.user and message.recipient != request.user:
        messages.error(request, 'You do not have permission to delete this message.')
        return redirect('dashboard:messages_list')
    
    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Message deleted successfully!')
        return redirect('dashboard:messages_list')
    
    context = {
        'page_title': 'Delete Message',
        'message': message,
    }
    return render(request, 'dashboard/message_confirm_delete.html', context)


# Notifications Views
@login_required
def notifications_list(request):
    """Notifications list"""
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = user_notifications.filter(is_read=False).count()
    
    # Mark as read if viewing
    user_notifications.filter(is_read=False).update(is_read=True)
    
    # Choose template based on user role
    if request.user.is_mentor:
        template = 'dashboard/notifications_list_mentor.html'
    else:
        template = 'dashboard/notifications_list.html'
    
    context = {
        'page_title': 'My Notifications',
        'notifications': user_notifications,
        'unread_count': unread_count,
    }
    return render(request, template, context)


@login_required
def notification_mark_read(request, notification_id):
    """Mark notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    messages.success(request, 'Notification marked as read.')
    return redirect('dashboard:notifications_list')


@login_required
def notification_delete(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    messages.success(request, 'Notification deleted.')
    return redirect('dashboard:notifications_list')
