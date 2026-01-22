"""
Train XGBoost models for multi-platform fake account detection.
This script trains separate models for Instagram, Twitter, and Facebook.
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from pathlib import Path
import logging
import warnings

warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_and_prepare_data(platform='Instagram'):
    """Load data for a specific platform and prepare it."""
    logger.info(f"Loading data for {platform}...")
    
    datasets_dir = Path(__file__).parent / 'datasets'
    
    # Load the main dataset
    df = pd.read_csv(datasets_dir / 'fake_social_media.csv')
    
    # Filter by platform
    df_platform = df[df['platform'] == platform].copy()
    
    if len(df_platform) == 0:
        logger.error(f"No data found for platform: {platform}")
        return None, None, None
    
    logger.info(f"Loaded {len(df_platform)} samples for {platform}")
    logger.info(f"Real accounts: {(df_platform['is_fake'] == 0).sum()}")
    logger.info(f"Fake accounts: {(df_platform['is_fake'] == 1).sum()}")
    
    # Map columns to our standardized feature names
    df_platform['follower_count'] = df_platform['followers']
    df_platform['following_count'] = df_platform['following']
    df_platform['post_count'] = df_platform['posts']
    df_platform['has_external_url'] = df_platform['suspicious_links_in_bio']
    df_platform['is_private'] = 0  # Not in dataset, default to public
    
    # Calculate engagement metrics (synthetic based on followers and posts)
    # In real scenario, this would come from actual engagement data
    np.random.seed(42)
    df_platform['avg_likes_per_post'] = (
        df_platform['follower_count'] * np.random.uniform(0.01, 0.05, len(df_platform))
    ).clip(lower=0)
    
    df_platform['avg_comments_per_post'] = (
        df_platform['avg_likes_per_post'] * np.random.uniform(0.05, 0.15, len(df_platform))
    ).clip(lower=0)
    
    # Calculate engagement rate
    df_platform['engagement_rate'] = (
        (df_platform['avg_likes_per_post'] + df_platform['avg_comments_per_post']) / 
        df_platform['follower_count'].replace(0, 1)
    ) * 100
    df_platform['engagement_rate'] = df_platform['engagement_rate'].clip(upper=500)
    
    # Handle infinite values in follower_following_ratio
    df_platform['follower_following_ratio'] = df_platform['follower_following_ratio'].replace([np.inf, -np.inf], 1000)
    df_platform['follower_following_ratio'] = df_platform['follower_following_ratio'].clip(upper=1000)
    
    # Define feature columns
    feature_columns = [
        'follower_count', 'following_count', 'post_count', 'bio_length',
        'has_profile_pic', 'has_external_url', 'avg_likes_per_post',
        'avg_comments_per_post', 'follower_following_ratio', 'engagement_rate', 'is_private'
    ]
    
    X = df_platform[feature_columns].copy()
    y = df_platform['is_fake'].copy()
    
    # Handle any remaining NaN or infinite values
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0)
    
    logger.info(f"Prepared {len(X)} samples with {len(feature_columns)} features")
    
    return X, y, feature_columns


def train_model(X_train, y_train, X_test, y_test, platform):
    """Train XGBoost model for a specific platform."""
    logger.info(f"Training XGBoost model for {platform}...")
    
    # Calculate class weights for imbalanced data
    class_counts = np.bincount(y_train)
    scale_pos_weight = class_counts[0] / class_counts[1] if class_counts[1] > 0 else 1.0
    
    logger.info(f"Class distribution - Real: {class_counts[0]}, Fake: {class_counts[1]}")
    logger.info(f"Scale pos weight: {scale_pos_weight:.2f}")
    
    # Initialize XGBoost classifier
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        objective='binary:logistic',
        eval_metric='logloss',
        random_state=42,
        use_label_encoder=False
    )
    
    # Train the model
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    logger.info(f"\n{platform} Model Performance:")
    logger.info(f"Accuracy: {accuracy:.4f}")
    logger.info(f"Precision: {precision:.4f}")
    logger.info(f"Recall: {recall:.4f}")
    logger.info(f"F1 Score: {f1:.4f}")
    
    logger.info(f"\nConfusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
    logger.info(f"\nClassification Report:\n{classification_report(y_test, y_pred, target_names=['Real', 'Fake'])}")
    
    return model


def save_model_artifacts(model, scaler, feature_names, platform, output_dir='ml_model'):
    """Save model, scaler, and feature names."""
    output_path = Path(__file__).parent.parent / output_dir
    output_path.mkdir(exist_ok=True)
    
    platform_lower = platform.lower()
    
    # Save XGBoost model
    model_path = output_path / f'{platform_lower}_model.json'
    model.save_model(str(model_path))
    logger.info(f"Model saved to: {model_path}")
    
    # Save scaler
    scaler_path = output_path / f'{platform_lower}_scaler.pkl'
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    logger.info(f"Scaler saved to: {scaler_path}")
    
    # Save feature names
    feature_names_path = output_path / f'{platform_lower}_feature_names.pkl'
    with open(feature_names_path, 'wb') as f:
        pickle.dump(feature_names, f)
    logger.info(f"Feature names saved to: {feature_names_path}")


def train_platform_model(platform):
    """Train model for a specific platform."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Training model for {platform}")
    logger.info(f"{'='*60}\n")
    
    # Load and prepare data
    X, y, feature_names = load_and_prepare_data(platform)
    
    if X is None:
        logger.error(f"Failed to load data for {platform}")
        return False
    
    # Check if we have enough samples for stratified split
    unique, counts = np.unique(y, return_counts=True)
    min_class_count = np.min(counts)
    
    if min_class_count < 2:
        logger.warning(f"⚠️ Class imbalance detected: minimum class has only {min_class_count} sample(s)")
        logger.warning("Using simple split without stratification")
        # Use simple split without stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=True
        )
    else:
        # Use stratified split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = train_model(X_train_scaled, y_train, X_test_scaled, y_test, platform)
    
    # Save artifacts
    save_model_artifacts(model, scaler, feature_names, platform)
    
    logger.info(f"✅ Successfully trained and saved {platform} model\n")
    return True


def main():
    """Train models for all platforms."""
    platforms = ['Instagram', 'Twitter', 'Facebook']
    
    logger.info("="*60)
    logger.info("Multi-Platform Fake Account Detection - Model Training")
    logger.info("="*60)
    
    results = {}
    for platform in platforms:
        success = train_platform_model(platform)
        results[platform] = success
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("Training Summary")
    logger.info("="*60)
    for platform, success in results.items():
        status = "✅ SUCCESS" if success else "❌ FAILED"
        logger.info(f"{platform}: {status}")
    
    # Check if all models were trained successfully
    if all(results.values()):
        logger.info("\n🎉 All platform models trained successfully!")
    else:
        logger.warning("\n⚠️ Some models failed to train. Check logs above.")


if __name__ == '__main__':
    main()
