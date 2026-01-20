from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.text import slugify
from .models import (
    Course,
    Enrollment,
    Certificate,
    CourseChapter,
    ChapterContent,
    ChapterProgress,
    Quiz,
    Question,
    Choice,
    QuizAttempt,
)
from .forms import CourseForm, ChapterForm, ChapterContentForm, QuizForm, QuestionForm, ChoiceForm


def index(request):
    """Course index page"""
    courses = Course.objects.filter(is_active=True)[:6]
    
    context = {
        'page_title': 'Courses',
        'courses': courses,
    }
    return render(request, 'training/index.html', context)


def _is_creator(user):
    return user.is_authenticated and (user.is_administrator or user.is_mentor or user.is_partner)


def _creator_base_template(user):
    if user.is_administrator:
        return 'dashboard/base_admin_dashboard.html'
    if user.is_mentor:
        return 'dashboard/base_mentor_dashboard.html'
    if user.is_partner:
        return 'dashboard/base_partner_dashboard.html'
    return 'base.html'


def _generate_unique_slug(model, base_slug):
    slug = base_slug
    counter = 1
    while model.objects.filter(slug=slug).exists():
        counter += 1
        slug = f"{base_slug}-{counter}"
    return slug


@login_required
def learning_dashboard(request):
    """Learning dashboard for enrolled students"""
    if not request.user.is_student:
        messages.error(request, 'Only students can access the learning dashboard.')
        return redirect('courses:index')
    
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    context = {
        'page_title': 'My Learning Dashboard',
        'enrollments': enrollments,
    }
    return render(request, 'training/learning_dashboard.html', context)


def course_detail(request, slug):
    """Course detail page"""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # Check if user is enrolled
    is_enrolled = False
    if request.user.is_authenticated and request.user.is_student:
        is_enrolled = Enrollment.objects.filter(
            course=course,
            student=request.user
        ).exists()
    
    chapters = course.chapters.prefetch_related('contents', 'quizzes__questions')
    context = {
        'page_title': course.title,
        'course': course,
        'is_enrolled': is_enrolled,
        'chapters': chapters,
    }
    return render(request, 'training/course_detail.html', context)


@login_required
def enroll(request, slug):
    """Enroll in a course"""
    if not request.user.is_student:
        messages.error(request, 'Only students can enroll in courses.')
        return redirect('courses:index')
    
    course = get_object_or_404(Course, slug=slug, is_active=True)
    
    # Check if already enrolled
    if Enrollment.objects.filter(course=course, student=request.user).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('courses:course_detail', slug=slug)
    
    Enrollment.objects.create(course=course, student=request.user)
    messages.success(request, f'Successfully enrolled in {course.title}!')
    return redirect('courses:learning_dashboard')


@login_required
def course_learn(request, slug):
    """Course learning page with video player and materials"""
    if not request.user.is_student:
        messages.error(request, 'Only students can access course materials.')
        return redirect('courses:index')
    
    course = get_object_or_404(Course, slug=slug, is_active=True)
    enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
    
    if not enrollment:
        messages.error(request, 'You must enroll in this course first.')
        return redirect('courses:course_detail', slug=slug)
    
    chapters = course.chapters.prefetch_related('contents', 'quizzes__questions__choices')
    progress_records = ChapterProgress.objects.filter(enrollment=enrollment)
    completed_chapter_ids = set(progress_records.filter(is_completed=True).values_list('chapter_id', flat=True))
    total_chapters = chapters.count()
    completed_chapters = ChapterProgress.objects.filter(enrollment=enrollment, is_completed=True).count()
    progress_percent = int((completed_chapters / total_chapters) * 100) if total_chapters else 0
    final_exam = course.quizzes.filter(quiz_type='final').first()
    final_attempt = None
    if final_exam:
        final_attempt = QuizAttempt.objects.filter(enrollment=enrollment, quiz=final_exam).first()
    
    context = {
        'page_title': f'Learning: {course.title}',
        'course': course,
        'enrollment': enrollment,
        'chapters': chapters,
        'completed_chapter_ids': completed_chapter_ids,
        'final_exam': final_exam,
        'final_attempt': final_attempt,
        'total_chapters': total_chapters,
        'completed_chapters': completed_chapters,
        'progress_percent': progress_percent,
    }
    return render(request, 'training/course_learn.html', context)


@login_required
def download_certificate(request, slug):
    """Download certificate for completed course"""
    if not request.user.is_student:
        messages.error(request, 'Only students can download certificates.')
        return redirect('courses:index')
    
    course = get_object_or_404(Course, slug=slug)
    enrollment = Enrollment.objects.filter(course=course, student=request.user).first()
    
    if not enrollment or not enrollment.is_completed:
        messages.error(request, 'Course must be completed to download certificate.')
        return redirect('courses:course_detail', slug=slug)
    
    certificate, created = Certificate.objects.get_or_create(
        enrollment=enrollment,
        defaults={'certificate_id': f"CERT-{enrollment.id}-{timezone.now().strftime('%Y%m%d')}"}
    )
    context = {
        'course': course,
        'enrollment': enrollment,
        'certificate': certificate,
    }
    template = get_template('training/certificate_pdf.html')
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), result)
    if pdf.err:
        messages.error(request, 'Unable to generate certificate PDF.')
        return redirect('courses:course_detail', slug=slug)

    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate-{course.slug}.pdf"'
    return response


@login_required
def course_create(request):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to create courses.')
        return redirect('courses:index')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            base_slug = slugify(course.title)[:60] or f"course-{request.user.id}"
            course.slug = _generate_unique_slug(Course, base_slug)
            course.created_by = request.user
            if request.user.is_mentor:
                course.instructor = request.user
            course.save()
            messages.success(request, 'Course created successfully.')
            return redirect('courses:course_manage', slug=course.slug)
    else:
        form = CourseForm()

    context = {
        'page_title': 'Create Course',
        'form': form,
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/course_form.html', context)


@login_required
def course_manage(request, slug):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to manage courses.')
        return redirect('courses:index')

    course = get_object_or_404(Course, slug=slug)
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to manage this course.')
        return redirect('courses:index')

    chapters = course.chapters.prefetch_related('contents', 'quizzes')
    final_exam = course.quizzes.filter(quiz_type='final').first()

    context = {
        'page_title': f'Manage Course: {course.title}',
        'course': course,
        'chapters': chapters,
        'final_exam': final_exam,
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/course_manage.html', context)


@login_required
def chapter_create(request, slug):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to add chapters.')
        return redirect('courses:index')

    course = get_object_or_404(Course, slug=slug)
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')

    if request.method == 'POST':
        form = ChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.course = course
            chapter.save()
            messages.success(request, 'Chapter added successfully.')
            return redirect('courses:course_manage', slug=slug)
    else:
        form = ChapterForm()

    context = {
        'page_title': 'Add Chapter',
        'form': form,
        'course': course,
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/chapter_form.html', context)


@login_required
def chapter_edit(request, chapter_id):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to edit chapters.')
        return redirect('courses:index')

    chapter = get_object_or_404(CourseChapter, id=chapter_id)
    course = chapter.course
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')

    if request.method == 'POST':
        form = ChapterForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            messages.success(request, 'Chapter updated successfully.')
            return redirect('courses:course_manage', slug=course.slug)
    else:
        form = ChapterForm(instance=chapter)

    context = {
        'page_title': 'Edit Chapter',
        'form': form,
        'course': course,
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/chapter_form.html', context)


@login_required
def chapter_delete(request, chapter_id):
    chapter = get_object_or_404(CourseChapter, id=chapter_id)
    course = chapter.course
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to delete chapters.')
        return redirect('courses:index')
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')
    if request.method == 'POST':
        chapter.delete()
        messages.info(request, 'Chapter deleted.')
    return redirect('courses:course_manage', slug=course.slug)


@login_required
def content_create(request, chapter_id):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to add content.')
        return redirect('courses:index')

    chapter = get_object_or_404(CourseChapter, id=chapter_id)
    course = chapter.course
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')

    if request.method == 'POST':
        form = ChapterContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.chapter = chapter
            content.save()
            messages.success(request, 'Content added successfully.')
            return redirect('courses:course_manage', slug=course.slug)
    else:
        form = ChapterContentForm()

    context = {
        'page_title': 'Add Content',
        'form': form,
        'course': course,
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/content_form.html', context)


@login_required
def content_edit(request, content_id):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to edit content.')
        return redirect('courses:index')

    content = get_object_or_404(ChapterContent, id=content_id)
    course = content.chapter.course
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')

    if request.method == 'POST':
        form = ChapterContentForm(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, 'Content updated successfully.')
            return redirect('courses:course_manage', slug=course.slug)
    else:
        form = ChapterContentForm(instance=content)

    context = {
        'page_title': 'Edit Content',
        'form': form,
        'course': course,
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/content_form.html', context)


@login_required
def content_delete(request, content_id):
    content = get_object_or_404(ChapterContent, id=content_id)
    course = content.chapter.course
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to delete content.')
        return redirect('courses:index')
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')
    if request.method == 'POST':
        content.delete()
        messages.info(request, 'Content deleted.')
    return redirect('courses:course_manage', slug=course.slug)


@login_required
def quiz_create(request, slug, chapter_id=None):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to add quizzes.')
        return redirect('courses:index')

    course = get_object_or_404(Course, slug=slug)
    chapter = None
    if chapter_id:
        chapter = get_object_or_404(CourseChapter, id=chapter_id, course=course)
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')

    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.course = course
            quiz.chapter = chapter
            if chapter:
                quiz.quiz_type = 'chapter'
            else:
                quiz.quiz_type = 'final'
            quiz.save()
            messages.success(request, 'Quiz created successfully.')
            return redirect('courses:course_manage', slug=course.slug)
    else:
        form = QuizForm()

    context = {
        'page_title': 'Add Quiz',
        'form': form,
        'course': course,
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/quiz_form.html', context)


@login_required
def quiz_edit(request, quiz_id):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to edit quizzes.')
        return redirect('courses:index')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')

    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            quiz_obj = form.save(commit=False)
            if quiz_obj.chapter:
                quiz_obj.quiz_type = 'chapter'
            else:
                quiz_obj.quiz_type = 'final'
            quiz_obj.save()
            messages.success(request, 'Quiz updated successfully.')
            return redirect('courses:course_manage', slug=course.slug)
    else:
        form = QuizForm(instance=quiz)

    context = {
        'page_title': 'Edit Quiz',
        'form': form,
        'course': course,
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/quiz_form.html', context)


@login_required
def quiz_delete(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to delete quizzes.')
        return redirect('courses:index')
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')
    if request.method == 'POST':
        quiz.delete()
        messages.info(request, 'Quiz deleted.')
    return redirect('courses:course_manage', slug=course.slug)


@login_required
def question_create(request, quiz_id):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to add questions.')
        return redirect('courses:index')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.course
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')

    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.save()
            messages.success(request, 'Question added. Now add choices.')
            return redirect('courses:choice_create', question_id=question.id)
    else:
        form = QuestionForm()

    context = {
        'page_title': 'Add Question',
        'form': form,
        'course': course,
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/question_form.html', context)


@login_required
def question_edit(request, question_id):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to edit questions.')
        return redirect('courses:index')

    question = get_object_or_404(Question, id=question_id)
    course = question.quiz.course
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question updated successfully.')
            return redirect('courses:course_manage', slug=course.slug)
    else:
        form = QuestionForm(instance=question)

    context = {
        'page_title': 'Edit Question',
        'form': form,
        'course': course,
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/question_form.html', context)


@login_required
def question_delete(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    course = question.quiz.course
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to delete questions.')
        return redirect('courses:index')
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')
    if request.method == 'POST':
        question.delete()
        messages.info(request, 'Question deleted.')
    return redirect('courses:course_manage', slug=course.slug)


@login_required
def choice_create(request, question_id):
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to add choices.')
        return redirect('courses:index')

    question = get_object_or_404(Question, id=question_id)
    course = question.quiz.course
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')

    if request.method == 'POST':
        form = ChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            messages.success(request, 'Choice added.')
            return redirect('courses:choice_create', question_id=question.id)
    else:
        form = ChoiceForm()

    context = {
        'page_title': 'Add Choice',
        'form': form,
        'course': course,
        'question': question,
        'choices': question.choices.all(),
        'base_template': _creator_base_template(request.user),
    }
    return render(request, 'training/manage/choice_form.html', context)


@login_required
def choice_delete(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id)
    course = choice.question.quiz.course
    if not _is_creator(request.user):
        messages.error(request, 'You do not have permission to delete choices.')
        return redirect('courses:index')
    if not request.user.is_administrator and course.created_by != request.user:
        messages.error(request, 'You do not have permission to edit this course.')
        return redirect('courses:index')
    if request.method == 'POST':
        choice.delete()
        messages.info(request, 'Choice deleted.')
    return redirect('courses:choice_create', question_id=choice.question.id)


def _check_completion(enrollment):
    chapters = enrollment.course.chapters.all()
    completed_chapters = ChapterProgress.objects.filter(enrollment=enrollment, is_completed=True).count()
    if chapters.count() != completed_chapters:
        return False
    quizzes = enrollment.course.quizzes.all()
    for quiz in quizzes:
        attempt = QuizAttempt.objects.filter(enrollment=enrollment, quiz=quiz, passed=True).first()
        if not attempt:
            return False
    enrollment.is_completed = True
    enrollment.completed_at = timezone.now()
    enrollment.save()
    Certificate.objects.get_or_create(
        enrollment=enrollment,
        defaults={'certificate_id': f"CERT-{enrollment.id}-{timezone.now().strftime('%Y%m%d')}"}
    )
    return True


@login_required
def mark_chapter_complete(request, chapter_id):
    if not request.user.is_student:
        messages.error(request, 'Only students can complete chapters.')
        return redirect('courses:index')

    chapter = get_object_or_404(CourseChapter, id=chapter_id)
    enrollment = Enrollment.objects.filter(course=chapter.course, student=request.user).first()
    if not enrollment:
        messages.error(request, 'You must enroll in this course first.')
        return redirect('courses:course_detail', slug=chapter.course.slug)

    progress, _ = ChapterProgress.objects.get_or_create(enrollment=enrollment, chapter=chapter)
    progress.is_completed = True
    progress.completed_at = timezone.now()
    progress.save()
    _check_completion(enrollment)
    messages.success(request, 'Chapter marked as completed.')
    return redirect('courses:course_learn', slug=chapter.course.slug)


@login_required
def take_quiz(request, quiz_id):
    if not request.user.is_student:
        messages.error(request, 'Only students can take quizzes.')
        return redirect('courses:index')

    quiz = get_object_or_404(Quiz, id=quiz_id)
    enrollment = Enrollment.objects.filter(course=quiz.course, student=request.user).first()
    if not enrollment:
        messages.error(request, 'You must enroll in this course first.')
        return redirect('courses:course_detail', slug=quiz.course.slug)

    if request.method == 'POST':
        total = quiz.questions.count()
        correct = 0
        for question in quiz.questions.all():
            answer = request.POST.get(f'question_{question.id}')
            if answer:
                try:
                    choice = Choice.objects.get(id=int(answer), question=question)
                    if choice.is_correct:
                        correct += 1
                except (Choice.DoesNotExist, ValueError):
                    pass
        score = int((correct / total) * 100) if total else 0
        passed = score >= quiz.pass_score
        QuizAttempt.objects.create(enrollment=enrollment, quiz=quiz, score=score, passed=passed)
        if passed:
            messages.success(request, f'Quiz passed with {score}%.')
        else:
            messages.error(request, f'Quiz failed with {score}%. Try again.')
        _check_completion(enrollment)
        return redirect('courses:course_learn', slug=quiz.course.slug)

    context = {
        'page_title': quiz.title,
        'quiz': quiz,
        'course': quiz.course,
    }
    return render(request, 'training/quiz_take.html', context)
