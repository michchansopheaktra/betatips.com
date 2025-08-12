from django.contrib import admin
from . models import Post, Category, Profile, Comment, AffiliateLink, Service

admin.site.register(Post)
admin.site.register(Category)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Service)
admin.site.register(AffiliateLink)