"""
ML prediction module for multi-platform fake account detection.
"""
import xgboost as xgb
import pickle
import numpy as np
import pandas as pd
import shap
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MultiPlatformPredictor:
    """Unified predictor for Instagram, Twitter, and Facebook."""
    
    def __init__(self, platform='instagram', model_dir='ml_model'):
        """
        Initialize predictor for a specific platform.
        
        Args:
            platform: 'instagram', 'twitter', or 'facebook'
            model_dir: Directory containing model files
        """
        self.platform = platform.lower()
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.explainer = None
    
    def load_model(self):
        """Load the trained model and preprocessor for the platform."""
        try:
            # Load XGBoost model
            model_path = self.model_dir / f'{self.platform}_model.json'
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
                
            self.model = xgb.XGBClassifier()
            self.model.load_model(str(model_path))
            logger.info(f"{self.platform.upper()} XGBoost model loaded successfully")
            
            # Load scaler
            scaler_path = self.model_dir / f'{self.platform}_scaler.pkl'
            if not scaler_path.exists():
                raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
                
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info(f"{self.platform.upper()} scaler loaded successfully")
            
            # Load feature names
            feature_names_path = self.model_dir / f'{self.platform}_feature_names.pkl'
            if not feature_names_path.exists():
                raise FileNotFoundError(f"Feature names file not found: {feature_names_path}")
                
            with open(feature_names_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            logger.info(f"{self.platform.upper()} feature names loaded successfully")
            
            # Initialize SHAP explainer
            self.explainer = shap.TreeExplainer(self.model)
            logger.info(f"{self.platform.upper()} SHAP explainer initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading {self.platform} model artifacts: {str(e)}")
            raise
    
    def is_model_loaded(self):
        """Check if all model artifacts are properly loaded."""
        return all([
            self.model is not None,
            self.scaler is not None,
            self.feature_names is not None,
            self.explainer is not None
        ])
    
    def predict(self, features_dict):
        """Make prediction and generate explanation."""
        try:
            if self.model is None:
                self.load_model()
            
            # Create feature array in the correct order
            feature_array = []
            for feature_name in self.feature_names:
                if feature_name in features_dict:
                    feature_array.append(features_dict[feature_name])
                else:
                    logger.warning(f"Missing feature: {feature_name}, using 0")
                    feature_array.append(0)
            
            # Convert to numpy array and reshape
            X = np.array(feature_array).reshape(1, -1)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            prediction = self.model.predict(X_scaled)[0]
            # Get probability scores
            probabilities = self.model.predict_proba(X_scaled)[0]
            
            # Get the confidence as the probability of the predicted class
            if prediction == 0:  # Real account
                confidence = probabilities[0]  # Probability of being real
                prediction_label = "Real"
            else:  # Fake account
                confidence = probabilities[1]  # Probability of being fake
                prediction_label = "Fake"
            
            logger.info(f"[{self.platform.upper()}] Prediction: {prediction_label}, Confidence: {confidence:.4f}")
            
            # Generate SHAP explanation
            shap_values = self.explainer.shap_values(X_scaled)
            
            # Get feature importance for explanation with interpretable text
            feature_importance = []
            for i, feature_name in enumerate(self.feature_names):
                importance = float(shap_values[0][i])
                feature_value = features_dict.get(feature_name, 0)
                
                # Create human-readable explanation
                explanation_text = self._create_feature_explanation(
                    feature_name, feature_value, importance, prediction_label
                )
                
                feature_importance.append({
                    'feature': feature_name,
                    'feature_display': self._format_feature_name(feature_name),
                    'value': feature_value,
                    'importance': importance,
                    'impact': 'Increases fake likelihood' if importance > 0 else 'Increases real likelihood',
                    'explanation': explanation_text
                })
            
            # Sort by absolute importance
            feature_importance.sort(key=lambda x: abs(x['importance']), reverse=True)
            
            return {
                'prediction': prediction_label,
                'confidence': float(confidence),
                'probabilities': {
                    'real': float(probabilities[0]),
                    'fake': float(probabilities[1])
                },
                'shap_explanation': feature_importance[:5],  # Top 5 features
                'all_shap_values': feature_importance,
                'all_features': features_dict,
                'platform': self.platform
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
    def _format_feature_name(self, feature_name):
        """Convert feature name to human-readable format."""
        name_map = {
            'follower_count': 'Followers',
            'following_count': 'Following',
            'post_count': 'Posts',
            'bio_length': 'Bio Length',
            'has_profile_pic': 'Profile Picture',
            'has_external_url': 'External URL',
            'avg_likes_per_post': 'Avg Likes per Post',
            'avg_comments_per_post': 'Avg Comments per Post',
            'follower_following_ratio': 'Follower/Following Ratio',
            'engagement_rate': 'Engagement Rate',
            'is_private': 'Private Account'
        }
        return name_map.get(feature_name, feature_name.replace('_', ' ').title())
    
    def _create_feature_explanation(self, feature_name, value, importance, prediction):
        """Create human-readable explanation for a feature's impact."""
        abs_importance = abs(importance)
        direction = "strongly suggests" if abs_importance > 0.5 else "suggests"
        account_type = "fake" if importance > 0 else "real"
        
        explanations = {
            'follower_count': f"Follower count of {value:,.0f} {direction} this is a {account_type} account",
            'following_count': f"Following {value:,.0f} accounts {direction} this is a {account_type} account",
            'post_count': f"Having {value:,.0f} posts {direction} this is a {account_type} account",
            'bio_length': f"Bio length of {value} characters {direction} this is a {account_type} account",
            'has_profile_pic': f"{'Having' if value else 'Not having'} a profile picture {direction} this is a {account_type} account",
            'has_external_url': f"{'Having' if value else 'Not having'} an external URL {direction} this is a {account_type} account",
            'avg_likes_per_post': f"Average of {value:.1f} likes per post {direction} this is a {account_type} account",
            'avg_comments_per_post': f"Average of {value:.1f} comments per post {direction} this is a {account_type} account",
            'follower_following_ratio': f"Follower-to-following ratio of {value:.2f} {direction} this is a {account_type} account",
            'engagement_rate': f"Engagement rate of {value:.2f}% {direction} this is a {account_type} account",
            'is_private': f"{'Private' if value else 'Public'} account status {direction} this is a {account_type} account",
        }
        
        return explanations.get(feature_name, f"{feature_name}: {value} {direction} {account_type}")
    
    def get_risk_level(self, confidence, prediction):
        """Determine risk level based on confidence and prediction."""
        if prediction == "Real":
            if confidence >= 0.9:
                return "Very Low Risk"
            elif confidence >= 0.7:
                return "Low Risk" 
            elif confidence >= 0.6:
                return "Moderate Risk"
            else:
                return "High Risk"
        else:  # Fake
            if confidence >= 0.9:
                return "Very High Risk"
            elif confidence >= 0.7:
                return "High Risk"
            elif confidence >= 0.6:
                return "Moderate Risk" 
            else:
                return "Low Risk"


# Backward compatibility: Keep InstagramPredictor as alias
InstagramPredictor = MultiPlatformPredictor


def analyze_account(features_dict, platform='instagram'):
    """Main function to analyze a social media account."""
    try:
        predictor = MultiPlatformPredictor(platform=platform)
        result = predictor.predict(features_dict)
        
        # Add risk level
        risk_level = predictor.get_risk_level(result['confidence'], result['prediction'])
        result['risk_level'] = risk_level
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed for {platform}: {str(e)}")
        raise Exception(f"Analysis failed: {str(e)}")