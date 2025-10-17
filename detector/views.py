"""
Django views for Instagram fake account detection.
"""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from .forms import ManualInputForm, URLInputForm
from .models import AnalysisHistory
from .scraper import scrape_instagram_profile
from .feature_engineering import FeatureEngineer
from .predictor import InstagramPredictor
from .utils import (
    validate_feature_data, 
    log_analysis_attempt, 
    sanitize_shap_data,
    get_risk_level,
    get_confidence_color
)

logger = logging.getLogger('detector')


def index(request):
    """Homepage view."""
    return render(request, 'index.html')


def manual_form(request):
    """Manual input form view."""
    if request.method == 'POST':
        form = ManualInputForm(request.POST)
        if form.is_valid():
            try:
                # Get cleaned form data
                form_data = form.cleaned_data
                
                # Convert form data to analysis format
                raw_data = {
                    'username': form_data['username'],
                    'follower_count': form_data['follower_count'],
                    'following_count': form_data['following_count'],
                    'post_count': form_data['post_count'],
                    'bio_length': form_data['bio_length'],
                    'has_profile_pic': form_data['has_profile_pic'],
                    'has_external_url': form_data['has_external_url'],
                    'avg_likes_per_post': form_data['avg_likes_per_post'],
                    'avg_comments_per_post': form_data['avg_comments_per_post'],
                    'is_private': False  # Manual input assumes public
                }
                
                # Process the analysis
                result = process_analysis(raw_data, 'manual')
                
                if result['success']:
                    # Store in session for results page
                    request.session['analysis_result'] = result['data']
                    log_analysis_attempt(form_data['username'], 'manual', True)
                    return redirect('results')
                else:
                    messages.error(request, result['error_message'])
                    log_analysis_attempt(form_data['username'], 'manual', False, result['error_message'])
                    
            except Exception as e:
                logger.error(f"Error processing manual form: {str(e)}")
                messages.error(request, "An error occurred while processing your request. Please try again.")
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ManualInputForm()
    
    return render(request, 'manual_form.html', {'form': form})


def url_form(request):
    """URL input form view."""
    if request.method == 'POST':
        form = URLInputForm(request.POST)
        if form.is_valid():
            try:
                instagram_url = form.cleaned_data['instagram_url']
                username = form.get_username_from_url()
                
                if not username:
                    messages.error(request, "Could not extract username from URL.")
                    return render(request, 'url_form.html', {'form': form})
                
                # Scrape Instagram profile
                scraped_data = scrape_instagram_profile(username)
                
                if scraped_data is None:
                    messages.error(request, 
                        "Failed to scrape Instagram profile. This could be due to:\n"
                        "• Rate limiting from Instagram\n"
                        "• Private account with limited access\n"
                        "• Network issues\n\n"
                        "Please try using the manual input method instead."
                    )
                    log_analysis_attempt(username, 'scraped', False, "Scraping failed")
                    return render(request, 'url_form.html', {'form': form})
                
                # Process the analysis
                result = process_analysis(scraped_data, 'scraped')
                
                if result['success']:
                    # Store in session for results page
                    request.session['analysis_result'] = result['data']
                    log_analysis_attempt(username, 'scraped', True)
                    return redirect('results')
                else:
                    messages.error(request, result['error_message'])
                    log_analysis_attempt(username, 'scraped', False, result['error_message'])
                    
            except Exception as e:
                logger.error(f"Error processing URL form: {str(e)}")
                messages.error(request, "An error occurred while processing your request. Please try again.")
        else:
            messages.error(request, "Please enter a valid Instagram URL.")
    else:
        form = URLInputForm()
    
    return render(request, 'url_form.html', {'form': form})


def results(request):
    """Results display view."""
    analysis_result = request.session.get('analysis_result')
    
    if not analysis_result:
        messages.error(request, "No analysis results found. Please perform an analysis first.")
        return redirect('index')
    
    # Add additional display formatting
    analysis_result['risk_level'] = get_risk_level(
        analysis_result['confidence_score'], 
        analysis_result['prediction']
    )
    analysis_result['confidence_color'] = get_confidence_color(
        analysis_result['confidence_score'], 
        analysis_result['prediction']
    )
    
    return render(request, 'results.html', {'result': analysis_result})


def history(request):
    """Analysis history view."""
    analyses = AnalysisHistory.objects.all().order_by('-created_at')[:50]  # Show last 50
    return render(request, 'history.html', {'analyses': analyses})


@require_http_methods(["POST"])
def save_analysis(request):
    """Save analysis result to history."""
    try:
        analysis_result = request.session.get('analysis_result')
        
        if not analysis_result:
            return JsonResponse({'success': False, 'error': 'No analysis result found'})
        
        # Create AnalysisHistory record
        analysis = AnalysisHistory.objects.create(
            username=analysis_result['username'],
            input_method=analysis_result['input_method'],
            follower_count=analysis_result['features']['follower_count'],
            following_count=analysis_result['features']['following_count'],
            post_count=analysis_result['features']['post_count'],
            bio_length=analysis_result['features']['bio_length'],
            has_profile_pic=bool(analysis_result['features']['has_profile_pic']),
            has_external_url=bool(analysis_result['features']['has_external_url']),
            avg_likes_per_post=analysis_result['features']['avg_likes_per_post'],
            avg_comments_per_post=analysis_result['features']['avg_comments_per_post'],
            follower_following_ratio=analysis_result['features']['follower_following_ratio'],
            engagement_rate=analysis_result['features']['engagement_rate'],
            is_private=bool(analysis_result['features']['is_private']),
            prediction=analysis_result['prediction'],
            confidence_score=analysis_result['confidence_score'],
            shap_explanation=analysis_result['shap_explanation']
        )
        
        logger.info(f"Saved analysis to history: {analysis.id}")
        return JsonResponse({'success': True, 'analysis_id': analysis.id})
        
    except Exception as e:
        logger.error(f"Error saving analysis: {str(e)}")
        return JsonResponse({'success': False, 'error': 'Failed to save analysis'})


def process_analysis(raw_data: dict, input_method: str) -> dict:
    """
    Process Instagram account analysis.
    
    Args:
        raw_data: Raw account data (scraped or manual)
        input_method: 'manual' or 'scraped'
        
    Returns:
        Dictionary with analysis results
    """
    try:
        # Validate and clean data
        cleaned_data = validate_feature_data(raw_data)
        
        # Engineer features
        feature_engineer = FeatureEngineer()
        features = feature_engineer.engineer_features(cleaned_data)
        
        # Validate features
        if not feature_engineer.validate_features(features):
            return {
                'success': False,
                'error_message': 'Invalid feature data detected. Please check your inputs.'
            }
        
        # Prepare features for model
        feature_array = feature_engineer.prepare_for_model(features)
        
        # Make prediction using new predictor interface
        from .predictor import analyze_account
        prediction_result = analyze_account(features)
        
        # Prepare result
        result = {
            'success': True,
            'data': {
                'username': cleaned_data['username'],
                'input_method': input_method,
                'prediction': prediction_result['prediction'],
                'confidence_score': prediction_result['confidence'] * 100,  # Convert to percentage
                'features': features,
                'shap_explanation': {
                    'top_features': [
                        {
                            'feature': feat['feature'],
                            'importance': feat['importance'],
                            'abs_importance': abs(feat['importance'])
                        }
                        for feat in prediction_result['shap_explanation']
                    ]
                },
                'feature_summaries': [
                    f"{feat['feature']}: {feat['impact']}" 
                    for feat in prediction_result['shap_explanation']
                ],
                'risk_level': prediction_result['risk_level']
            }
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error in process_analysis: {str(e)}")
        return {
            'success': False,
            'error_message': f'Analysis failed: {str(e)}'
        }


# API Views for AJAX requests
@csrf_exempt
@require_http_methods(["POST"])
def api_analyze_manual(request):
    """API endpoint for manual analysis."""
    try:
        data = json.loads(request.body)
        result = process_analysis(data, 'manual')
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'prediction': result['data']['prediction'],
                'confidence': result['data']['confidence_score'],
                'features': result['data']['features'],
                'explanation': result['data']['feature_summaries']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error_message']
            })
            
    except Exception as e:
        logger.error(f"Error in API manual analysis: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        })


@csrf_exempt
@require_http_methods(["POST"])
def api_analyze_url(request):
    """API endpoint for URL analysis."""
    try:
        data = json.loads(request.body)
        url = data.get('url', '')
        
        # Extract username from URL
        from .utils import extract_username_from_url
        username = extract_username_from_url(url)
        
        if not username:
            return JsonResponse({
                'success': False,
                'error': 'Invalid Instagram URL'
            })
        
        # Scrape profile
        scraped_data = scrape_instagram_profile(username)
        
        if scraped_data is None:
            return JsonResponse({
                'success': False,
                'error': 'Failed to scrape Instagram profile'
            })
        
        # Process analysis
        result = process_analysis(scraped_data, 'scraped')
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'prediction': result['data']['prediction'],
                'confidence': result['data']['confidence_score'],
                'features': result['data']['features'],
                'explanation': result['data']['feature_summaries']
            })
        else:
            return JsonResponse({
                'success': False,
                'error': result['error_message']
            })
            
    except Exception as e:
        logger.error(f"Error in API URL analysis: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        })
