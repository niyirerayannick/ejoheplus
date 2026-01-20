from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from django.db.models import Prefetch
from .models import (
    Career,
    CareerProgram,
    CareerQuestion,
    CareerOption,
    CareerOptionWeight,
    CareerDiscoveryResponse,
    CareerDiscoveryAnswer,
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
    questions = CareerQuestion.objects.filter(is_active=True).prefetch_related('options').order_by('order', 'id')
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

        if step >= total:
            return redirect('careers:discovery_results')
        return redirect(f"{request.path}?step={step + 1}")

    progress = int((step / total) * 100)
    context = {
        'page_title': 'Career Discovery',
        'question': question,
        'step': step,
        'total': total,
        'progress': progress,
        'level': request.session.get('career_discovery_level', ''),
    }
    return render(request, 'careers/discovery_questionnaire.html', context)


def discovery_results(request):
    answers = request.session.get('career_discovery_answers', {})
    if not answers:
        return redirect('careers:discovery_intro')

    if not request.session.session_key:
        request.session.save()

    option_ids = [int(option_id) for option_id in answers.values()]
    option_qs = CareerOption.objects.filter(id__in=option_ids).prefetch_related(
        Prefetch('career_weights', queryset=CareerOptionWeight.objects.select_related('career'))
    )

    scores = {}
    reasons = {}
    for option in option_qs:
        for weight in option.career_weights.all():
            scores.setdefault(weight.career, 0)
            reasons.setdefault(weight.career, [])
            scores[weight.career] += weight.weight
            if option.explanation:
                reasons[weight.career].append(option.explanation)
            else:
                reasons[weight.career].append(option.text)

    sorted_careers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_score = sorted_careers[0][1] if sorted_careers else 1

    level_key = 'advanced' if level in ['A-Level', 'S4', 'S5', 'S6'] else 'ordinary' if level in ['O-Level', 'S1', 'S2', 'S3'] else ''
    results = []
    for career, score in sorted_careers:
        percentage = int((score / top_score) * 100)
        program_qs = CareerProgram.objects.filter(career=career)
        if level_key:
            program_qs = program_qs.filter(level=level_key)
        results.append({
            'career': career,
            'score': score,
            'percentage': percentage,
            'reasons': reasons.get(career, [])[:3],
            'programs': program_qs[:3],
        })

    best_matches = [item for item in results if item['percentage'] >= 75][:3]
    alternatives = [item for item in results if item['percentage'] < 75][:3]

    level = request.session.get('career_discovery_level', '')
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
    }
    return render(request, 'careers/discovery_results.html', context)
