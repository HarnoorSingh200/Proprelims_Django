# quiz/urls.py

from django.views.generic import TemplateView
from django.urls import path
from . import views
from django.contrib import sitemaps
from django.contrib.sitemaps.views import sitemap
from quiz.sitemaps import BlogPostSitemap, StaticViewSitemap

sitemaps_dict = {
    'blog': BlogPostSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('', views.home, name='home'),
    # Existing Quiz Views
    path('quiz/<int:quiz_id>/', views.quiz_detail, name='quiz_detail'),
    path('quiz/<int:quiz_id>/start/', views.quiz_paginated, name='quiz_paginated'),
    path('quiz/<int:quiz_id>/submit/', views.quiz_submit_paginated, name='quiz_submit_paginated'),
    path('quiz/<int:quiz_id>/solutions/', views.quiz_solutions, name='quiz_solutions'),

    # New Advance Quiz Views
    path('advance-quiz/<int:quiz_id>/', views.advance_quiz_detail, name='advance_quiz_detail'),
    path('advance-quiz/<int:quiz_id>/start/', views.advance_quiz_paginated, name='advance_quiz_paginated'),
    path('advance-quiz/<int:quiz_id>/submit/', views.advance_quiz_submit_paginated, name='advance_quiz_submit_paginated'),
    path('advance-quiz/<int:quiz_id>/solutions/', views.advance_quiz_solutions, name='advance_quiz_solutions'),

    # Search
    path('quizzes/', views.search_quizzes, name='quiz_search_page'),
    path('quizzes/filter/', views.quiz_list_partial, name='quiz_list_partial'),

    # Legal
    path('privacy/', TemplateView.as_view(template_name='static_pages/privacy_policy.html'), name='privacy_policy'),
    path('terms/', TemplateView.as_view(template_name='static_pages/terms_of_service.html'), name='terms_of_service'),
    path('accept-terms/', views.accept_terms, name='accept_terms'),
    path('contact/', TemplateView.as_view(template_name='static_pages/contact.html'), name='contact_page'),

    # Profile
    path('profile/', views.user_profile, name='user_profile'),

    # Blog URLs
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<int:post_id>/', views.blog_detail, name='blog_detail'),
    path('blog/<int:post_id>/like/', views.like_blog_post, name='like_blog_post'),

    # Report Issue
    path('quiz/<int:quiz_id>/report/', views.report_issue, name='report_issue'),

    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps_dict}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),

    # Super Quiz Views
    path('super-quiz/<int:quiz_id>/', views.super_quiz_detail, name='super_quiz_detail'),
    path('super-quiz/<int:quiz_id>/instructions/', views.super_quiz_instructions, name='super_quiz_instructions'),
    path('super-quiz/<int:quiz_id>/start/', views.super_quiz_paginated, name='super_quiz_paginated'),
    path('super-quiz/<int:quiz_id>/submit/', views.super_quiz_submit_paginated, name='super_quiz_submit_paginated'),
    path('super-quiz/<int:quiz_id>/solutions/', views.super_quiz_solutions, name='super_quiz_solutions'),
]