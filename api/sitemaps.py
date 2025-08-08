from django.contrib.sitemaps import Sitemap
from .models import Post, Category, Profile  # or User if you're using auth.User
from taggit.models import Tag  # If you're using django-taggit
from django.urls import reverse

class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Category.objects.all()

    def location(self, obj):
        return reverse('category_posts', args=[obj.slug])


class AuthorSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Profile.objects.all()

    def location(self, obj):
        return reverse('profile_detail', args=[obj.user.username])


class TagSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Tag.objects.all()

    def location(self, obj):
        return reverse('tagged_posts', args=[obj.slug])
