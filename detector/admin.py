"""
Django admin configuration for detector app.
"""
from django.contrib import admin
from .models import AnalysisHistory


@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    """Admin interface for AnalysisHistory model."""
    
    list_display = [
        'username', 
        'prediction', 
        'confidence_score', 
        'input_method',
        'created_at'
    ]
    
    list_filter = [
        'prediction',
        'input_method', 
        'is_private',
        'has_profile_pic',
        'has_external_url',
        'created_at'
    ]
    
    search_fields = ['username']
    
    readonly_fields = [
        'created_at', 
        'updated_at',
        'follower_following_ratio',
        'engagement_rate'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('username', 'input_method', 'created_at', 'updated_at')
        }),
        ('Account Features', {
            'fields': (
                'follower_count', 
                'following_count', 
                'post_count',
                'bio_length',
                'has_profile_pic',
                'has_external_url',
                'is_private'
            )
        }),
        ('Engagement Metrics', {
            'fields': (
                'avg_likes_per_post',
                'avg_comments_per_post',
                'follower_following_ratio',
                'engagement_rate'
            )
        }),
        ('Prediction Results', {
            'fields': (
                'prediction',
                'confidence_score',
                'shap_explanation'
            )
        })
    )
    
    ordering = ['-created_at']
    
    def get_queryset(self, request):
        """Optimize queryset for admin."""
        return super().get_queryset(request).select_related()
