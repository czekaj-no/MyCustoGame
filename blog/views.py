from django.shortcuts import render, get_object_or_404
from .models import Post

def blog_list(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    return render(request, 'blog/blog_list.html', {'posts': posts})

def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    return render(request, 'blog/blog_detail.html', {'post': post})

from django.core.paginator import Paginator
from django.db.models import Q

def blog_list(request):
    query = request.GET.get('q')  # wyszukiwarka
    posts = Post.objects.filter(published=True).order_by('-created_at')

    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    paginator = Paginator(posts, 5)  # 5 postów na stronę
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/blog_list.html', {
        'page_obj': page_obj,
        'query': query
    })

