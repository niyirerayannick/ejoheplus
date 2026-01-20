from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from dashboard.models import Article
from opportunities.models import Opportunity


def home(request):
    """Homepage view"""
    latest_opportunities = Opportunity.objects.filter(
        is_active=True
    ).order_by('?')[:4]
    context = {
        'page_title': 'Home - EjoHePlus',
        'latest_opportunities': latest_opportunities,
    }
    return render(request, 'home.html', context)


def about(request):
    """About us page"""
    context = {
        'page_title': 'About Us - EjoHePlus',
    }
    return render(request, 'about.html', context)


def blog_list(request):
    query = request.GET.get('q', '').strip()
    articles = Article.objects.filter(status='published').order_by('-published_at', '-created_at')
    if query:
        articles = articles.filter(title__icontains=query)

    paginator = Paginator(articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    category_qs = Article.objects.filter(status='published').exclude(category='').values_list('category', flat=True)
    categories = {}
    for cat in category_qs:
        categories[cat] = categories.get(cat, 0) + 1

    tags = []
    for article in articles:
        if article.tags:
            tags += [t.strip() for t in article.tags.split(',') if t.strip()]
    tag_set = sorted(set(tags))

    recent_posts = Article.objects.filter(status='published').order_by('-published_at', '-created_at')[:3]

    context = {
        'page_title': 'Articles',
        'page_obj': page_obj,
        'query': query,
        'categories': categories,
        'tags': tag_set,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog/index.html', context)


def blog_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, status='published')
    recent_posts = Article.objects.filter(status='published').exclude(id=article.id).order_by('-published_at', '-created_at')[:3]
    tag_list = []
    if article.tags:
        tag_list = [t.strip() for t in article.tags.split(',') if t.strip()]
    context = {
        'page_title': article.title,
        'article': article,
        'recent_posts': recent_posts,
        'tag_list': tag_list,
    }
    return render(request, 'blog/detail.html', context)
