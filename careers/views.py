from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count
from .models import (
    Career,
    CareerProgram,
    CareerQuestion,
    CareerOption,
    CareerOptionWeight,
    CareerDiscoveryResponse,
    CareerDiscoveryAnswer,
    CareerAssessment,
    CareerAnswer,
    CareerResult,
    CareerRecommendation,
)


def career_list(request):
    """List all careers with search and filters"""
    careers = Career.objects.all()
    
    query = request.GET.get('search', '')
    if query:
        careers = careers.filter(title__icontains=query)
    
    context = {
        'page_title': 'Careers Library',
        'careers': careers,
        'search_query': query,
    }
    return render(request, 'careers/list.html', context)


def career_detail(request, slug):
    """Career detail page"""
    career = get_object_or_404(Career, slug=slug)
    
    context = {
        'page_title': career.title,
        'career': career,
    }
    return render(request, 'careers/detail.html', context)


def discovery_intro(request):
    context = {
        'page_title': 'Career Discovery',
    }
    return render(request, 'careers/discovery_intro.html', context)


def discovery_questionnaire(request):
    questions = CareerQuestion.objects.filter(is_active=True).prefetch_related('options').order_by('order', 'id')[:30]
    total = questions.count()
    if total == 0:
        messages.error(request, 'Career discovery questions are not yet available.')
        return redirect('careers:discovery_intro')

    step = int(request.GET.get('step', '1'))
    step = max(1, min(step, total))
    question = questions[step - 1]

    if request.method == 'POST':
        selected_option_id = request.POST.get('option')
        level = request.POST.get('level', '').strip()
        if level:
            request.session['career_discovery_level'] = level
        if not selected_option_id:
            if level and step == 1:
                return redirect(f"{request.path}?step=1")
            messages.error(request, 'Please select an answer to continue.')
            return redirect(f"{request.path}?step={step}")

        answers = request.session.get('career_discovery_answers', {})
        answers[str(question.id)] = selected_option_id
        request.session['career_discovery_answers'] = answers

        if not request.session.session_key:
            request.session.save()

        assessment_id = request.session.get('career_assessment_id')
        assessment = None
        if assessment_id:
            assessment = CareerAssessment.objects.filter(id=assessment_id).first()
        if assessment is None:
            anonymous = request.session.get('career_discovery_anonymous', False)
            user = request.user if request.user.is_authenticated and not anonymous else None
            assessment = CareerAssessment.objects.create(
                user=user,
                session_key=request.session.session_key or '',
                level=level,
                status='in_progress',
            )
            request.session['career_assessment_id'] = assessment.id
        elif level and assessment.level != level:
            assessment.level = level
            assessment.save(update_fields=['level'])

        option = question.options.filter(id=selected_option_id).first()
        if option:
            CareerAnswer.objects.update_or_create(
                assessment=assessment,
                question=question,
                defaults={'score': option.value},
            )

        if step >= total:
            return redirect('careers:discovery_results')
        return redirect(f"{request.path}?step={step + 1}")

    progress = int((step / total) * 100)
    answers = request.session.get('career_discovery_answers', {})
    selected_option_id = answers.get(str(question.id))
    context = {
        'page_title': 'Career Discovery',
        'question': question,
        'step': step,
        'total': total,
        'progress': progress,
        'selected_option_id': int(selected_option_id) if selected_option_id else None,
        'level': request.session.get('career_discovery_level', ''),
    }
    return render(request, 'careers/discovery_questionnaire.html', context)


def discovery_history(request):
    assessments_qs = CareerAssessment.objects.filter(status='completed')
    if request.user.is_authenticated:
        assessments_qs = assessments_qs.filter(user=request.user)
    else:
        if not request.session.session_key:
            request.session.save()
        assessments_qs = assessments_qs.filter(session_key=request.session.session_key)

    assessments = []
    for assessment in assessments_qs.select_related('result'):
        code = ''
        if getattr(assessment, 'result', None):
            code = f"{assessment.result.primary_code}{assessment.result.secondary_code}{assessment.result.tertiary_code}"
        assessments.append({
            'date_started': assessment.date_started,
            'level': assessment.level,
            'code': code,
            'status_label': assessment.get_status_display(),
        })

    context = {
        'page_title': 'Career Discovery History',
        'assessments': assessments,
    }
    return render(request, 'careers/discovery_history.html', context)


def discovery_results(request):
    answers = request.session.get('career_discovery_answers', {})
    if not answers:
        return redirect('careers:discovery_intro')

    if not request.session.session_key:
        request.session.save()

    option_ids = [int(option_id) for option_id in answers.values()]
    option_qs = CareerOption.objects.filter(id__in=option_ids).select_related('question')

    riasec_labels = {
        'R': 'Realistic',
        'I': 'Investigative',
        'A': 'Artistic',
        'S': 'Social',
        'E': 'Enterprising',
        'C': 'Conventional',
    }
    riasec_explanations = {
        'R': 'You enjoy hands-on activities, practical tasks, and working with tools or systems.',
        'I': 'You enjoy exploring ideas, solving problems, and learning how things work.',
        'A': 'You enjoy creativity, self-expression, and artistic or innovative activities.',
        'S': 'You enjoy helping, teaching, and working with people.',
        'E': 'You enjoy leading, persuading, and taking initiative to achieve goals.',
        'C': 'You enjoy organizing, planning, and working with data or structured tasks.',
    }

    riasec_scores = {key: 0 for key in riasec_labels}
    for option in option_qs:
        if not option.question_id:
            continue
        riasec_key = option.question.category
        if riasec_key in riasec_scores:
            riasec_scores[riasec_key] += option.value

    ranked_riasec = sorted(riasec_scores.items(), key=lambda x: x[1], reverse=True)
    top_three = [item[0] for item in ranked_riasec[:3]]
    riasec_code = ''.join(top_three)
    question_counts = {
        item['category']: item['total']
        for item in CareerQuestion.objects.filter(is_active=True).values('category').annotate(total=Count('id'))
    }
    riasec_breakdown = []
    for code, score in ranked_riasec:
        max_score = (question_counts.get(code, 1) * 5)
        percent = int((score / max_score) * 100) if max_score else 0
        riasec_breakdown.append({
            'code': code,
            'label': riasec_labels.get(code, code),
            'score': score,
            'percent': percent,
        })
    top_interest_cards = [
        {
            'code': code,
            'label': riasec_labels.get(code, code),
            'explanation': riasec_explanations.get(code, ''),
        }
        for code in top_three
    ]

    level = request.session.get('career_discovery_level', '')
    level_key = 'advanced' if level in ['A-Level', 'S4', 'S5', 'S6'] else 'ordinary' if level in ['O-Level', 'S1', 'S2', 'S3'] else ''

    assessment = None
    assessment_id = request.session.get('career_assessment_id')
    if assessment_id:
        assessment = CareerAssessment.objects.filter(id=assessment_id).first()
    if assessment is None:
        anonymous = request.session.get('career_discovery_anonymous', False)
        user = request.user if request.user.is_authenticated and not anonymous else None
        assessment = CareerAssessment.objects.create(
            user=user,
            session_key=request.session.session_key or 'anonymous',
            level=level,
            status='completed',
            date_completed=timezone.now(),
        )
        request.session['career_assessment_id'] = assessment.id
    else:
        assessment.status = 'completed'
        assessment.date_completed = timezone.now()
        assessment.level = level
        assessment.save(update_fields=['status', 'date_completed', 'level'])

    CareerResult.objects.update_or_create(
        assessment=assessment,
        defaults={
            'realistic_score': riasec_scores.get('R', 0),
            'investigative_score': riasec_scores.get('I', 0),
            'artistic_score': riasec_scores.get('A', 0),
            'social_score': riasec_scores.get('S', 0),
            'enterprising_score': riasec_scores.get('E', 0),
            'conventional_score': riasec_scores.get('C', 0),
            'primary_code': top_three[0],
            'secondary_code': top_three[1],
            'tertiary_code': top_three[2],
        },
    )

    results = []
    careers = Career.objects.exclude(riasec_primary='').exclude(riasec_primary__isnull=True)
    max_score = 7
    for career in careers:
        secondary_codes = [code.strip().upper() for code in career.riasec_secondary.split(',') if code.strip()]
        score = 0
        if career.riasec_primary:
            if career.riasec_primary == top_three[0]:
                score += 5
            elif career.riasec_primary == top_three[1]:
                score += 3
            elif career.riasec_primary == top_three[2]:
                score += 2
        for code in secondary_codes:
            if code in top_three:
                score += 1
        percentage = int((score / max_score) * 100)
        program_qs = CareerProgram.objects.filter(career=career)
        if level_key:
            program_qs = program_qs.filter(level=level_key)
        reasons = [riasec_explanations.get(code) for code in top_three if code in riasec_explanations]
        results.append({
            'career': career,
            'score': score,
            'percentage': percentage,
            'reasons': [reason for reason in reasons if reason][:2],
            'programs': program_qs[:3],
        })

    results = sorted(results, key=lambda x: x['percentage'], reverse=True)
    best_matches = [item for item in results if item['percentage'] >= 70][:4]
    alternatives = [item for item in results if item['percentage'] < 70][:4]

    response = CareerDiscoveryResponse.objects.create(
        session_key=request.session.session_key or 'anonymous',
        level=level,
    )
    for question_id, option_id in answers.items():
        CareerDiscoveryAnswer.objects.create(
            response=response,
            question_id=int(question_id),
            option_id=int(option_id),
        )

    context = {
        'page_title': 'Career Discovery Results',
        'best_matches': best_matches,
        'alternatives': alternatives,
        'level': level,
        'level_key': level_key,
        'riasec_scores': riasec_breakdown,
        'riasec_code': riasec_code,
        'riasec_explanations': riasec_explanations,
        'top_interest_cards': top_interest_cards,
    }
    return render(request, 'careers/discovery_results.html', context)
