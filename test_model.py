#!/usr/bin/env python
"""
Test the model loading and prediction functionality.
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_detector.settings')
django.setup()

from detector.predictor import InstagramPredictor
from detector.feature_engineering import FeatureEngineer
import numpy as np

def test_model_loading():
    """Test if the model loads correctly."""
    try:
        print("Testing model loading...")
        predictor = InstagramPredictor()
        
        if predictor.is_model_loaded():
            print("✅ Model loaded successfully!")
            return True
        else:
            print("❌ Model failed to load")
            return False
            
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return False

def test_prediction():
    """Test a sample prediction."""
    try:
        print("\nTesting prediction...")
        
        # Sample Instagram account data (similar to your test)
        sample_data = {
            'username': 'test_account',
            'follower_count': 86000000,
            'following_count': 533,
            'post_count': 2183,
            'bio_length': 20,
            'has_profile_pic': True,
            'has_external_url': False,
            'avg_likes_per_post': 1500000,
            'avg_comments_per_post': 5000,
            'is_private': False
        }
        
        # Engineer features
        feature_engineer = FeatureEngineer()
        features = feature_engineer.engineer_features(sample_data)
        feature_array = feature_engineer.prepare_for_model(features)
        
        print(f"Engineered features: {features}")
        
        # Make prediction
        predictor = InstagramPredictor()
        prediction, confidence, shap_explanation = predictor.predict(feature_array)
        
        print(f"✅ Prediction successful!")
        print(f"   Result: {prediction}")
        print(f"   Confidence: {confidence:.2%}")
        print(f"   Top features influencing prediction:")
        
        if shap_explanation and 'top_features' in shap_explanation:
            for i, feature in enumerate(shap_explanation['top_features'][:3]):
                direction = "↑" if feature['importance'] > 0 else "↓"
                print(f"     {i+1}. {feature['feature']}: {feature['importance']:.4f} {direction}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in prediction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🔍 Instagram Fake Account Detection - Model Test")
    print("=" * 50)
    
    # Test 1: Model Loading
    model_loaded = test_model_loading()
    
    if model_loaded:
        # Test 2: Prediction
        prediction_works = test_prediction()
        
        if prediction_works:
            print("\n🎉 All tests passed! The system is ready to use.")
        else:
            print("\n⚠️  Model loads but prediction failed.")
    else:
        print("\n❌ Model loading failed. Check model files.")
    
    print("=" * 50)
