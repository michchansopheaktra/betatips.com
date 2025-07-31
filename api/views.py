import json
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from .models import Post, Category, Profile, User, Comment
from taggit.models import Tag
from django.db.models import Q
from .forms import PostForm, UserForm, ProfileForm, CategoryForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from .forms import RegisterForm
from django import forms
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

def is_admin(user):
    return user.is_authenticated and user.is_staff

@login_required
@user_passes_test(is_admin)
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)  # ← add request.FILES
        if form.is_valid():
            post = form.save()
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    return render(request, 'add_post.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug)

    if request.method == 'POST':
        form = PostForm(request.POST or None, request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)

    return render(request, 'add_post.html', {
        'form': form,
        'edit_mode': True,
        'post': post,
    })

@login_required
@user_passes_test(is_admin)
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post_list')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def category_edit(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('post_list')  # or redirect to category list page
    else:
        form = CategoryForm(instance=category)

    return render(request, 'add_category.html', {'form': form, 'edit_mode': True})

@login_required
@user_passes_test(is_admin)
def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if request.method == 'POST':
        category.delete()
        return redirect('post_list')  # Or wherever you want after delete

    return render(request, 'category_confirm_delete.html', {'category': category})


@login_required
@user_passes_test(is_admin)
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug)
    if request.method == 'POST':
        post.delete()
        return redirect('post_list')
    return render(request, 'post_confirm_delete.html', {'post': post})

@login_required
def profile_detail(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = Post.objects.filter(author=user)

    total_posts = user_posts.count()
    total_categories = Category.objects.filter(posts__in=user_posts).distinct().count()

    context = {
        'profile_user': user,
        'total_posts': total_posts,
        'total_categories': total_categories,
    }
    return render(request, 'profile_detail.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile_detail', username=request.user.username)
    else:
        u_form = UserForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)
    return render(request, 'edit_profile.html', {'u_form': u_form, 'p_form': p_form})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after register
            return redirect('post_list')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def post_search(request):
    query = request.GET.get('q', '')
    results = Post.objects.filter(
        Q(title__icontains=query) | Q(content__icontains=query)
    ).order_by('-created_at') if query else Post.objects.none()

    paginator = Paginator(results, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()

    return render(request, 'post_search.html', {
        'query': query,
        'page_obj': page_obj,
        'categories': categories,
    })

def tagged_posts(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    posts = Post.objects.filter(tags=tag).order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    return render(request, 'tag_posts.html', {
        'tag': tag,
        'page_obj': page_obj,
        'categories': categories,
    })

def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "_post_list.html", {
            "page_obj": page_obj,
            "categories": categories
        })
    return render(request, "post_list.html", {
        "page_obj": page_obj,
        "categories": categories
    })


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category).order_by('-created_at')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    return render(request, "category_posts.html", {
        "category": category,
        "page_obj": page_obj,
        "categories": categories,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.views += 1
    post.save()

    related_posts = Post.objects.filter(category=post.category).exclude(id=post.id)[:6]
    related_posts_side = Post.objects.filter(category=post.category).exclude(id=post.id).distinct()[:4]
    categories = Category.objects.all()

    return render(request, "post_detail.html", {
        "post": post,
        "related_posts": related_posts,
        "categories": categories,
        "related_posts_side": related_posts_side,
    })


def contact_page(request):
    return render(request, 'pages/contact.html')

def privacy_page(request):
    return render(request, 'pages/policy.html')

def about_page(request):
    return render(request, 'pages/about.html')