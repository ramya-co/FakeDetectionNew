"""
Utility functions for Instagram fake account detection.
"""
import logging
import re
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger('detector')


def clean_username(username: str) -> str:
    """
    Clean and validate Instagram username.
    
    Args:
        username: Raw username input
        
    Returns:
        Cleaned username
    """
    username = username.strip().lower()
    
    # Remove @ if present
    if username.startswith('@'):
        username = username[1:]
    
    return username


def validate_instagram_url(url: str) -> bool:
    """
    Validate Instagram profile URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid Instagram URL, False otherwise
    """
    patterns = [
        r'^https?://(?:www\.)?instagram\.com/([a-zA-Z0-9._]{1,30})/?$',
        r'^https?://(?:www\.)?instagram\.com/([a-zA-Z0-9._]{1,30})/?\?.*$',
    ]
    
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    
    return False


def extract_username_from_url(url: str) -> Optional[str]:
    """
    Extract username from Instagram URL.
    
    Args:
        url: Instagram profile URL
        
    Returns:
        Username or None if extraction fails
    """
    patterns = [
        r'instagram\.com/([a-zA-Z0-9._]{1,30})/?$',
        r'instagram\.com/([a-zA-Z0-9._]{1,30})/?\?.*$',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def format_number(number: int) -> str:
    """
    Format large numbers for display (e.g., 1.2K, 1.5M).
    
    Args:
        number: Number to format
        
    Returns:
        Formatted string
    """
    if number >= 1_000_000:
        return f"{number / 1_000_000:.1f}M"
    elif number >= 1_000:
        return f"{number / 1_000:.1f}K"
    else:
        return str(number)


def format_percentage(value: float) -> str:
    """
    Format percentage for display.
    
    Args:
        value: Percentage value (0-100)
        
    Returns:
        Formatted percentage string
    """
    return f"{value:.1f}%"


def validate_feature_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean feature data.
    
    Args:
        data: Raw feature data
        
    Returns:
        Cleaned and validated feature data
    """
    cleaned_data = {}
    
    # Integer fields
    int_fields = ['follower_count', 'following_count', 'post_count', 'bio_length']
    for field in int_fields:
        try:
            value = int(data.get(field, 0))
            cleaned_data[field] = max(0, value)  # Ensure non-negative
        except (ValueError, TypeError):
            logger.warning(f"Invalid value for {field}: {data.get(field)}, using 0")
            cleaned_data[field] = 0
    
    # Float fields
    float_fields = ['avg_likes_per_post', 'avg_comments_per_post']
    for field in float_fields:
        try:
            value = float(data.get(field, 0.0))
            cleaned_data[field] = max(0.0, value)  # Ensure non-negative
        except (ValueError, TypeError):
            logger.warning(f"Invalid value for {field}: {data.get(field)}, using 0.0")
            cleaned_data[field] = 0.0
    
    # Boolean fields
    bool_fields = ['has_profile_pic', 'has_external_url', 'is_private']
    for field in bool_fields:
        cleaned_data[field] = bool(data.get(field, False))
    
    # String fields
    string_fields = ['username']
    for field in string_fields:
        cleaned_data[field] = str(data.get(field, '')).strip()
    
    return cleaned_data


def get_risk_level(confidence: float, prediction: str) -> str:
    """
    Get risk level based on prediction confidence.
    
    Args:
        confidence: Prediction confidence (0-1)
        prediction: Prediction label ('Real' or 'Fake')
        
    Returns:
        Risk level string
    """
    if prediction == "Fake":
        if confidence >= 0.9:
            return "Very High Risk"
        elif confidence >= 0.7:
            return "High Risk"
        elif confidence >= 0.6:
            return "Medium Risk"
        else:
            return "Low Risk"
    else:  # Real
        if confidence >= 0.9:
            return "Very Low Risk"
        elif confidence >= 0.7:
            return "Low Risk"
        elif confidence >= 0.6:
            return "Medium Risk"
        else:
            return "High Risk"


def get_confidence_color(confidence: float, prediction: str) -> str:
    """
    Get color class for confidence display.
    
    Args:
        confidence: Prediction confidence (0-1)
        prediction: Prediction label ('Real' or 'Fake')
        
    Returns:
        CSS color class
    """
    if prediction == "Fake":
        if confidence >= 0.7:
            return "text-danger"  # Red for high confidence fake
        else:
            return "text-warning"  # Orange for low confidence fake
    else:  # Real
        if confidence >= 0.7:
            return "text-success"  # Green for high confidence real
        else:
            return "text-warning"  # Orange for low confidence real


def log_analysis_attempt(username: str, method: str, success: bool, error: str = None, platform: str = 'instagram'):
    """
    Log analysis attempt for debugging and monitoring.
    
    Args:
        username: Username being analyzed
        method: Analysis method ('manual' or 'scraped')
        success: Whether analysis was successful
        error: Error message if unsuccessful
        platform: Social media platform ('instagram', 'twitter', 'facebook')
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if success:
        logger.info(f"[{timestamp}] [{platform.upper()}] Analysis successful - Username: {username}, Method: {method}")
    else:
        logger.error(f"[{timestamp}] [{platform.upper()}] Analysis failed - Username: {username}, Method: {method}, Error: {error}")


def sanitize_shap_data(shap_explanation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize SHAP explanation data for JSON serialization.
    
    Args:
        shap_explanation: Raw SHAP explanation dictionary
        
    Returns:
        Sanitized SHAP explanation
    """
    try:
        sanitized = {}
        
        if 'top_features' in shap_explanation:
            sanitized['top_features'] = []
            for feature in shap_explanation['top_features']:
                sanitized_feature = {
                    'feature': str(feature.get('feature', '')),
                    'importance': float(feature.get('importance', 0.0)),
                    'abs_importance': float(feature.get('abs_importance', 0.0))
                }
                sanitized['top_features'].append(sanitized_feature)
        
        if 'all_features' in shap_explanation:
            sanitized['all_features'] = []
            for feature in shap_explanation['all_features']:
                sanitized_feature = {
                    'feature': str(feature.get('feature', '')),
                    'importance': float(feature.get('importance', 0.0)),
                    'abs_importance': float(feature.get('abs_importance', 0.0))
                }
                sanitized['all_features'].append(sanitized_feature)
        
        return sanitized
        
    except Exception as e:
        logger.error(f"Error sanitizing SHAP data: {str(e)}")
        return {}
