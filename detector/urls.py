"""
URL configuration for the detector app.
"""
from django.urls import path, include
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('manual/', views.manual_form, name='manual_form'),
    path('url/', views.url_form, name='url_form'),
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
