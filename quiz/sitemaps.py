from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost

class BlogPostSitemap(Sitemap):
    changefreq = "weekly"  # Google uses this as a hint
    priority = 0.7

    def items(self):
        return BlogPost.objects.all()

    def location(self, obj):
        return reverse('blog_detail', kwargs={'post_id': obj.post_id})

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'monthly'

    def items(self):
        return ['home', 'blog_list', 'privacy_policy', 'terms_of_service', 'contact_page']

    def location(self, item):
        return reverse(item)
