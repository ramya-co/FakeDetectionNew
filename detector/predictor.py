"""
ML prediction module for Instagram fake account detection.
"""
import xgboost as xgb
import pickle
import numpy as np
import pandas as pd
import shap
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class InstagramPredictor:
    def __init__(self, model_dir='ml_model'):
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.explainer = None
        
    def load_model(self):
        """Load the trained model and preprocessor."""
        try:
            # Load XGBoost model
            model_path = self.model_dir / 'instagram_model.json'
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")
                
            self.model = xgb.XGBClassifier()
            self.model.load_model(str(model_path))
            logger.info("XGBoost model loaded successfully")
            
            # Load scaler
            scaler_path = self.model_dir / 'scaler.pkl'
            if not scaler_path.exists():
                raise FileNotFoundError(f"Scaler file not found: {scaler_path}")
                
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            logger.info("Scaler loaded successfully")
            
            # Load feature names
            feature_names_path = self.model_dir / 'feature_names.pkl'
            if not feature_names_path.exists():
                raise FileNotFoundError(f"Feature names file not found: {feature_names_path}")
                
            with open(feature_names_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            logger.info("Feature names loaded successfully")
            
            # Initialize SHAP explainer
            # Create dummy data for explainer initialization
            dummy_data = np.random.random((100, len(self.feature_names)))
            self.explainer = shap.TreeExplainer(self.model)
            logger.info("SHAP explainer initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading model artifacts: {str(e)}")
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
            # Get probability scores - THIS IS THE FIX!
            probabilities = self.model.predict_proba(X_scaled)[0]
            
            # FIXED: Get the confidence as the probability of the predicted class
            if prediction == 0:  # Real account
                confidence = probabilities[0]  # Probability of being real
                prediction_label = "Real"
            else:  # Fake account
                confidence = probabilities[1]  # Probability of being fake
                prediction_label = "Fake"
            
            logger.info(f"Prediction: {prediction_label}, Confidence: {confidence:.4f}")
            
            # Generate SHAP explanation
            shap_values = self.explainer.shap_values(X_scaled)
            
            # Get feature importance for explanation
            feature_importance = []
            for i, feature_name in enumerate(self.feature_names):
                importance = float(shap_values[0][i])
                feature_importance.append({
                    'feature': feature_name,
                    'value': features_dict.get(feature_name, 0),
                    'importance': importance,
                    'impact': 'Increases fake likelihood' if importance > 0 else 'Increases real likelihood'
                })
            
            # Sort by absolute importance
            feature_importance.sort(key=lambda x: abs(x['importance']), reverse=True)
            
            return {
                'prediction': prediction_label,
                'confidence': float(confidence),  # This is now correct!
                'probabilities': {
                    'real': float(probabilities[0]),
                    'fake': float(probabilities[1])
                },
                'shap_explanation': feature_importance[:5],  # Top 5 features
                'all_features': features_dict
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
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

def analyze_account(features_dict):
    """Main function to analyze an Instagram account."""
    try:
        predictor = InstagramPredictor()
        result = predictor.predict(features_dict)
        
        # Add risk level
        risk_level = predictor.get_risk_level(result['confidence'], result['prediction'])
        result['risk_level'] = risk_level
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise Exception(f"Analysis failed: {str(e)}")
