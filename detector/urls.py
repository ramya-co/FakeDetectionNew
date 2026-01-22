"""
URL configuration for the detector app - Multi-platform support.
"""
from django.urls import path, include
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    
    # Instagram URLs
    path('instagram/manual/', views.manual_form, name='instagram_manual'),
    path('instagram/url/', views.url_form, name='instagram_url'),
    path('manual/', views.manual_form, name='manual_form'),  # Legacy support
    path('url/', views.url_form, name='url_form'),  # Legacy support
    
    # Twitter URLs
    path('twitter/manual/', views.twitter_manual, name='twitter_manual'),
    path('twitter/url/', views.twitter_url, name='twitter_url'),
    
    # Facebook URLs
    path('facebook/manual/', views.facebook_manual, name='facebook_manual'),
    path('facebook/url/', views.facebook_url, name='facebook_url'),
    
    # Results and History
    path('results/', views.results, name='results'),
    path('history/', views.history, name='history'),
    
    # Actions
    path('save-analysis/', views.save_analysis, name='save_analysis'),
    
    # API endpoints
    path('api/analyze/manual/', views.api_analyze_manual, name='api_analyze_manual'),
    path('api/analyze/url/', views.api_analyze_url, name='api_analyze_url'),
    
    # Simulation URLs
    path('simulation/', include('detector.simulation_urls')),
]
