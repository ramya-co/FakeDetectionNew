"""
URL patterns for Instagram simulation functionality.
"""
from django.urls import path
from . import simulation_views, dashboard_views

app_name = 'simulation'

urlpatterns = [
    # Simulation intro and flow
    path('', simulation_views.simulation_intro, name='intro'),
    path('create-account/', simulation_views.create_account, name='create_account'),
    path('instagram/', simulation_views.instagram_clone, name='instagram_clone'),
    
    # User profile and actions
    path('profile/', simulation_views.user_profile, name='user_profile'),
    path('end/', simulation_views.end_simulation, name='end_simulation'),
    
    # API endpoints for Instagram clone functionality
    path('create-post/', simulation_views.create_post, name='create_post'),
    path('toggle-like/<int:post_id>/', simulation_views.toggle_like, name='toggle_like'),
    path('add-comment/<int:post_id>/', simulation_views.add_comment, name='add_comment'),
    
    # Analytics Dashboard
    path('dashboard/', dashboard_views.dashboard, name='dashboard'),
    path('dashboard/user/<int:user_id>/', dashboard_views.user_detail, name='user_detail'),
    
    # Dashboard API endpoints
    path('api/dashboard-data/', dashboard_views.dashboard_data_api, name='dashboard_data_api'),
    path('api/dashboard-stats/', dashboard_views.dashboard_stats_api, name='dashboard_stats_api'),
    path('api/reanalyze/<int:user_id>/', dashboard_views.reanalyze_user, name='reanalyze_user'),
    path('api/user-history/<int:user_id>/', dashboard_views.user_prediction_history, name='user_prediction_history'),
]
