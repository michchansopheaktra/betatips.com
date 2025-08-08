from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve
from django.urls import re_path

from django.contrib.sitemaps.views import sitemap
from api.sitemaps import PostSitemap, CategorySitemap, AuthorSitemap, TagSitemap

from django.conf import settings
from django.conf.urls.static import static


sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
    'authors': AuthorSitemap,
    'tags': TagSitemap,
    
}


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("api.urls")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('sitemap-categories.xml', sitemap, {'sitemaps': {'categories': CategorySitemap}}, name='sitemap-categories'),
    path('sitemap-authors.xml', sitemap, {'sitemaps': {'authors': AuthorSitemap}}, name='sitemap-authors'),
    path('sitemap-tags.xml', sitemap, {'sitemaps': {'tags': TagSitemap}}, name='sitemap-tags'),
    
    # Serve media files manually when DEBUG = False
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),

    # Serve static files manually when DEBUG = False
    re_path(r'^static/(?P<path>.*)$', serve, {
        'document_root': settings.STATIC_ROOT,
    }),
]

# Optional: Only use static() helper in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
