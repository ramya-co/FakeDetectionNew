"""
Dashboard views for real-time analytics.
"""
import logging
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from detector.models import SimulatedUser, SimulatedPost, SimulatedLike, SimulatedComment, SimulatedActivity, SimulatedPrediction
from .simulation_analyzer import analyzer

logger = logging.getLogger(__name__)


def dashboard(request):
    """
    Main analytics dashboard showing all simulated users and predictions.
    """
    # Get initial data for dashboard
    dashboard_data = analyzer.get_dashboard_data()
    
    context = {
        'dashboard_data': dashboard_data,
        'last_updated': timezone.now().isoformat(),
    }
    
    return render(request, 'simulation/dashboard.html', context)


@require_http_methods(["GET"])
def dashboard_data_api(request):
    """
    API endpoint for dashboard data (used for AJAX polling).
    Returns JSON with all dashboard information for real-time updates.
    """
    try:
        data = analyzer.get_dashboard_data()
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return JsonResponse({'error': 'Failed to get dashboard data'}, status=500)


def user_detail(request, user_id):
    """
    Detailed view of a specific simulated user with SHAP explanations.
    """
    try:
        user_detail_data = analyzer.get_user_detail(user_id)
        
        if not user_detail_data:
            return render(request, 'simulation/user_detail.html', {
                'error': 'User not found or error loading data'
            })
        
        context = {
            'user_detail': user_detail_data,
        }
        
        return render(request, 'simulation/user_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error getting user detail for {user_id}: {str(e)}")
        return render(request, 'simulation/user_detail.html', {
            'error': 'Error loading user data'
        })


@require_http_methods(["POST"])
def reanalyze_user(request, user_id):
    """
    Force re-analysis of a specific user.
    Used by the "Re-analyze Now" button in user detail page.
    """
    try:
        # Verify user exists
        user = get_object_or_404(SimulatedUser, id=user_id)
        
        # Force re-analysis
        prediction = analyzer.force_reanalyze(user_id)
        
        if prediction:
            return JsonResponse({
                'success': True,
                'prediction': prediction.prediction,
                'confidence': prediction.confidence_percentage,
                'predicted_at': prediction.predicted_at.isoformat(),
                'message': 'Analysis completed successfully!'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Analysis failed. User may not have enough activity.'
            })
    
    except Exception as e:
        logger.error(f"Error re-analyzing user {user_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Error during re-analysis. Please try again.'
        }, status=500)


@require_http_methods(["GET"])
def user_prediction_history(request, user_id):
    """
    API endpoint to get prediction history for a specific user.
    """
    try:
        user = get_object_or_404(SimulatedUser, id=user_id)
        predictions = user.predictions.all().order_by('-predicted_at')
        
        history_data = []
        for pred in predictions:
            history_data.append({
                'prediction': pred.prediction,
                'confidence': pred.confidence_percentage,
                'predicted_at': pred.predicted_at.isoformat(),
                'risk_level': pred.risk_level,
                'is_latest': pred.is_latest
            })
        
        return JsonResponse({
            'success': True,
            'username': user.username,
            'history': history_data
        })
        
    except Exception as e:
        logger.error(f"Error getting prediction history for user {user_id}: {str(e)}")
        return JsonResponse({'error': 'Failed to get prediction history'}, status=500)


@require_http_methods(["GET"])
def dashboard_stats_api(request):
    """
    API endpoint for just the statistics (lighter than full dashboard data).
    """
    try:
        dashboard_data = analyzer.get_dashboard_data()
        
        # Return only stats and chart data, not individual users
        return JsonResponse({
            'stats': dashboard_data['stats'],
            'chart_data': dashboard_data['chart_data'],
            'last_updated': dashboard_data['last_updated']
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        return JsonResponse({'error': 'Failed to get dashboard stats'}, status=500)
