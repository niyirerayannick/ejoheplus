from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Q
from .models import Opportunity, Application


def opportunity_list(request):
    """List all opportunities with filters"""
    opportunities = Opportunity.objects.filter(is_active=True)

    category_filter = request.GET.get('category', '').strip().lower()
    categories = []
    category_map = {}
    for opportunity in opportunities:
        raw_category = opportunity.category.strip() if opportunity.category else opportunity.get_type_display()
        category_slug = slugify(raw_category)
        if category_slug not in category_map:
            category_map[category_slug] = {'name': raw_category, 'categories': set(), 'types': set()}
            categories.append({'name': raw_category, 'slug': category_slug})
        if opportunity.category:
            category_map[category_slug]['categories'].add(opportunity.category)
        else:
            category_map[category_slug]['types'].add(opportunity.type)

    if category_filter:
        if category_filter in category_map:
            filters = category_map[category_filter]
            opportunities = opportunities.filter(
                Q(category__in=filters['categories']) | Q(type__in=filters['types'])
            )
        else:
            opportunities = opportunities.none()

    search_query = request.GET.get('search', '')
    if search_query:
        opportunities = opportunities.filter(title__icontains=search_query)

    if not category_filter:
        opportunities = opportunities.order_by('?')

    context = {
        'page_title': 'Opportunities',
        'opportunities': opportunities,
        'categories': categories,
        'active_category': category_filter,
        'search_query': search_query,
    }
    return render(request, 'opportunities/list.html', context)


def jobs_page(request):
    """Jobs page"""
    return render(request, 'opportunities/jobs.html', {'page_title': 'Jobs'})


def scholarships_page(request):
    """Scholarships page"""
    return render(request, 'opportunities/scholarships.html', {'page_title': 'Scholarships'})


def internships_page(request):
    """Internships page"""
    return render(request, 'opportunities/internships.html', {'page_title': 'Internships'})


def opportunity_detail(request, slug):
    """Opportunity detail page"""
    opportunity = get_object_or_404(Opportunity, slug=slug, is_active=True)
    
    # Check if user has already applied
    has_applied = False
    if request.user.is_authenticated and request.user.is_student:
        has_applied = Application.objects.filter(
            opportunity=opportunity,
            student=request.user
        ).exists()
    
    context = {
        'page_title': opportunity.title,
        'opportunity': opportunity,
        'has_applied': has_applied,
    }
    return render(request, 'opportunities/detail.html', context)


@login_required
def apply(request, slug):
    """Apply for an opportunity"""
    if not request.user.is_student:
        messages.error(request, 'Only students can apply for opportunities.')
        return redirect('opportunities:list')
    
    opportunity = get_object_or_404(Opportunity, slug=slug, is_active=True)
    
    if request.method == 'POST':
        # Check if already applied
        if Application.objects.filter(opportunity=opportunity, student=request.user).exists():
            messages.warning(request, 'You have already applied for this opportunity.')
            return redirect('opportunities:detail', slug=slug)
        
        cover_letter = request.POST.get('cover_letter', '')
        if cover_letter:
            Application.objects.create(
                opportunity=opportunity,
                student=request.user,
                cover_letter=cover_letter
            )
            messages.success(request, 'Application submitted successfully!')
            return redirect('opportunities:detail', slug=slug)
        else:
            messages.error(request, 'Please provide a cover letter.')
    
    return redirect('opportunities:detail', slug=slug)
