import json
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect, render
from .models import Post, Category, Profile, User, Comment, AffiliateLink, Service
from taggit.models import Tag
from django.db.models import Q, Count
from .forms import PostForm, UserForm, ProfileForm, CategoryForm, AffiliateLinkForm, ServiceForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, LogoutView
from .forms import RegisterForm
from django import forms
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

import os
import zipfile
from django.conf import settings
from .forms import ZipUploadForm
from .models import ZipUpload
from django.core.files.storage import FileSystemStorage
from django.contrib import messages 
import uuid
from datetime import datetime

import random


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
            form = CategoryForm()  # reset form after save
    else:
        form = CategoryForm()

    # Get all categories to display on the page
    categories = Category.objects.annotate(post_count=Count('posts'))

    return render(request, 'add_category.html', {
        'form': form,
        'categories': categories,
    })

@login_required
@user_passes_test(is_admin)
def category_edit(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_add')  # or redirect to category list page
    else:
        form = CategoryForm(instance=category)

    return render(request, 'add_category.html', {'form': form, 'edit_mode': True})

@login_required
@user_passes_test(is_admin)
def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if request.method == 'POST':
        category.delete()
        return redirect('category_add')  # Or wherever you want after delete

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

    paginator = Paginator(results, 24)
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
    paginator = Paginator(posts, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    categories = Category.objects.all()
    return render(request, 'tag_posts.html', {
        'tag': tag,
        'page_obj': page_obj,
        'categories': categories,
    })

def post_list(request):
    posts = Post.objects.all().order_by('?')
    paginator = Paginator(posts, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # categories = Category.objects.all()

    categories = Category.objects.annotate(post_count=Count('posts'))
    
    # categories_count = Category.objects.annotate(post_count=Count('post'))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, "_post_list.html", {
            "page_obj": page_obj,
            "categories": categories,
            # "categories_count": categories_count,
        })
    return render(request, "post_list.html", {
        "page_obj": page_obj,
        "categories": categories,
        # "categories_count": categories_count,
    })


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category).order_by('-created_at')
    paginator = Paginator(posts, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # categories = Category.objects.all()
    categories = Category.objects.annotate(post_count=Count('posts'))
    return render(request, "category_posts.html", {
        "category": category,
        "page_obj": page_obj,
        "categories": categories,
    })


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.views += 1
    post.save()

    related_posts = Post.objects.filter(category=post.category).order_by('?')[:12]
    related_posts_side = Post.objects.filter(category=post.category).order_by('?').distinct()[:4]
    categories = Category.objects.annotate(post_count=Count('posts'))
    # categories = Category.objects.all()
    # affiliate link
    affiliate_links = AffiliateLink.objects.all()

    return render(request, "post_detail.html", {
        "post": post,
        "related_posts": related_posts,
        "categories": categories,
        "related_posts_side": related_posts_side,
        "affiliate_links": affiliate_links,
        'meta_title': post.title,
        'meta_description': post.excerpt or post.content[:160],
        'meta_keywords': ', '.join(tag.name for tag in post.tags.all()),
    })


def contact_page(request):
    categories = Category.objects.annotate(post_count=Count('posts'))
    return render(request, 'pages/contact.html',{
        "categories": categories,
    })

def privacy_page(request):
    categories = Category.objects.annotate(post_count=Count('posts'))
    return render(request, 'pages/policy.html',{
        "categories": categories,
    })

def about_page(request):
    categories = Category.objects.annotate(post_count=Count('posts'))

    services = Service.objects.all()
    return render(request, 'pages/about.html',{
        "categories": categories,
        "services": services,
    })

def products_page(request):
    categories = Category.objects.annotate(post_count=Count('posts'))

    services = Service.objects.all()
    return render(request, 'pages/products.html',{
        "categories": categories,
        "services": services,
    })

ZIP_UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'zips')
@login_required
@user_passes_test(is_admin)
def upload_zip(request):
    form = ZipUploadForm()  # ✅ Ensure form is defined

    download_url = None  # Default: nothing to show

    if request.method == 'POST':
        form = ZipUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['zip_file']
            filename = uploaded_file.name.replace(" ", "_")
            unique_name = f"{os.path.splitext(filename)[0]}_{uuid.uuid4().hex[:8]}.zip"
            save_path = os.path.join(settings.MEDIA_ROOT, 'zips', unique_name)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            download_url = os.path.join(settings.MEDIA_URL, 'zips', unique_name)
            messages.success(request, 'ZIP file uploaded successfully.')

    # ✅ Handle listing and pagination
    zip_dir = os.path.join(settings.MEDIA_ROOT, 'zips')
    zip_files = []
    if os.path.exists(zip_dir):
        zip_files = sorted(os.listdir(zip_dir), reverse=True)

    paginator = Paginator(zip_files, 16)  # 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    zip_files_info = []
    for f in page_obj:
        file_path = os.path.join(zip_dir, f)
        file_stat = os.stat(file_path)
        zip_files_info.append({
            "name": f,
            "url": os.path.join(settings.MEDIA_URL, "zips", f),
            "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
            "uploaded_at": datetime.fromtimestamp(file_stat.st_mtime),
        })

    return render(request, "upload_zip.html", {
        "form": form,
        "download_url": download_url,
        "zip_files": zip_files_info,
        "page_obj": page_obj,
    })

@login_required
@user_passes_test(is_admin)
def delete_zip(request, filename):
    file_path = os.path.join(ZIP_UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        messages.success(request, f"{filename} deleted.")
    else:
        messages.error(request, "File not found.")
    return redirect('upload_zip')

# affiliate link
@login_required
@user_passes_test(is_admin)
def affiliate_link_create(request):
    if request.method == 'POST':
        form = AffiliateLinkForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = AffiliateLinkForm()  # Reset form after save

    else:
        form = AffiliateLinkForm()

    # Get all existing affiliate links
    affiliate_links = AffiliateLink.objects.all()

    return render(request, 'affiliate_link_form.html', {
        'form': form,
        'affiliate_links': affiliate_links
    })
@login_required
@user_passes_test(is_admin)
def affiliate_link_update(request, pk):
    link = get_object_or_404(AffiliateLink, pk=pk)
    if request.method == "POST":
        form = AffiliateLinkForm(request.POST, request.FILES, instance=link)
        if form.is_valid():
            form.save()
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = AffiliateLinkForm(instance=link)
    return render(request, 'affiliate_link_form.html', {'form': form})
@login_required
@user_passes_test(is_admin)
def affiliate_link_delete(request, pk):
    link = get_object_or_404(AffiliateLink, pk=pk)
    
    if request.method == "POST":
        # Build full file path safely
        if link.image:
            file_path = os.path.join(settings.MEDIA_ROOT, link.image.name)  # link.image.name is a str
            if os.path.exists(file_path):
                os.remove(file_path)
        link.delete()
        messages.success(request, f'Affiliate link "{link.title}" deleted.')
        return redirect('affiliate_link_create')

    return render(request, 'affiliate_link_confirm_delete.html', {'link': link})

# All Services
@login_required
@user_passes_test(is_admin)
def service_create_and_list(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            form = ServiceForm()  # reset form after saving
    else:
        form = ServiceForm()

    services = Service.objects.all()

    return render(request, 'service_form_and_list.html', {
        'form': form,
        'services': services,
    })


# Update an existing service
@login_required
@user_passes_test(is_admin)
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service_create_and_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'service_form_and_list.html', {'form': form})

# Delete a service with confirmation
@login_required
@user_passes_test(is_admin)
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('service_create_and_list')
    return render(request, 'service_confirm_delete.html', {'service': service})
