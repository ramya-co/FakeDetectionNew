"""
Feature engineering for Instagram fake account detection.
"""
import numpy as np
import pandas as pd
import logging
from typing import Dict, Any, List

logger = logging.getLogger('detector')


class FeatureEngineer:
    """Class to handle feature engineering for Instagram account data."""
    
    def __init__(self):
        """Initialize feature engineer."""
        self.feature_names = [
            'follower_count',
            'following_count', 
            'post_count',
            'bio_length',
            'has_profile_pic',
            'has_external_url',
            'avg_likes_per_post',
            'avg_comments_per_post',
            'follower_following_ratio',
            'engagement_rate',
            'is_private'
        ]
    
    def engineer_features(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Engineer features from raw Instagram data.
        
        Args:
            raw_data: Raw scraped or manual Instagram data
            
        Returns:
            Dictionary with engineered features
        """
        try:
            features = {}
            
            # Basic features (direct mapping)
            features['follower_count'] = int(raw_data.get('follower_count', 0))
            features['following_count'] = int(raw_data.get('following_count', 0))
            features['post_count'] = int(raw_data.get('post_count', 0))
            features['bio_length'] = int(raw_data.get('bio_length', 0))
            features['has_profile_pic'] = int(bool(raw_data.get('has_profile_pic', False)))
            features['has_external_url'] = int(bool(raw_data.get('has_external_url', False)))
            features['avg_likes_per_post'] = float(raw_data.get('avg_likes_per_post', 0.0))
            features['avg_comments_per_post'] = float(raw_data.get('avg_comments_per_post', 0.0))
            features['is_private'] = int(bool(raw_data.get('is_private', False)))
            
            # Engineered features
            features['follower_following_ratio'] = self._calculate_follower_following_ratio(
                features['follower_count'], 
                features['following_count']
            )
            
            features['engagement_rate'] = self._calculate_engagement_rate(
                features['avg_likes_per_post'],
                features['avg_comments_per_post'],
                features['follower_count']
            )
            
            logger.info("Successfully engineered features")
            return features
            
        except Exception as e:
            logger.error(f"Error engineering features: {str(e)}")
            raise
    
    def _calculate_follower_following_ratio(self, followers: int, following: int) -> float:
        """
        Calculate follower to following ratio.
        
        Args:
            followers: Number of followers
            following: Number of following
            
        Returns:
            Follower/following ratio
        """
        if following == 0:
            return float(100.0)  # Cap at 100 for accounts with 0 following
        
        ratio = followers / following
        # Cap very high ratios to prevent outliers
        return min(ratio, 1000.0)
    
    def _calculate_engagement_rate(self, avg_likes: float, avg_comments: float, followers: int) -> float:
        """
        Calculate engagement rate as percentage.
        
        Args:
            avg_likes: Average likes per post
            avg_comments: Average comments per post
            followers: Number of followers
            
        Returns:
            Engagement rate as percentage
        """
        if followers == 0:
            return 0.0
        
        total_engagement = avg_likes + avg_comments
        engagement_rate = (total_engagement / followers) * 100
        
        # Cap engagement rate to reasonable maximum (500%)
        return min(engagement_rate, 500.0)
    
    def prepare_for_model(self, features: Dict[str, Any]) -> np.ndarray:
        """
        Prepare features for model input.
        
        Args:
            features: Dictionary of engineered features
            
        Returns:
            NumPy array ready for model prediction
        """
        try:
            # Ensure all required features are present
            feature_values = []
            for feature_name in self.feature_names:
                if feature_name not in features:
                    logger.warning(f"Missing feature: {feature_name}, using default value 0")
                    feature_values.append(0.0)
                else:
                    feature_values.append(float(features[feature_name]))
            
            return np.array(feature_values).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Error preparing features for model: {str(e)}")
            raise
    
    def get_feature_names(self) -> List[str]:
        """Get list of feature names in correct order."""
        return self.feature_names.copy()
    
    def validate_features(self, features: Dict[str, Any]) -> bool:
        """
        Validate that all required features are present and have valid values.
        
        Args:
            features: Dictionary of features to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            for feature_name in self.feature_names:
                if feature_name not in features:
                    logger.warning(f"Missing required feature: {feature_name}")
                    return False
                
                value = features[feature_name]
                if not isinstance(value, (int, float, bool)):
                    logger.warning(f"Invalid type for feature {feature_name}: {type(value)}")
                    return False
                
                # Check for negative values where they don't make sense
                if feature_name in ['follower_count', 'following_count', 'post_count', 'bio_length', 
                                   'avg_likes_per_post', 'avg_comments_per_post'] and value < 0:
                    logger.warning(f"Negative value for feature {feature_name}: {value}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating features: {str(e)}")
            return False


def engineer_features_from_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to engineer features from raw data.
    
    Args:
        data: Raw Instagram account data
        
    Returns:
        Dictionary with engineered features
    """
    engineer = FeatureEngineer()
    return engineer.engineer_features(data)
