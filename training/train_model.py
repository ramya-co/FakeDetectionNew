"""
Train XGBoost model for Instagram fake account detection.
This script loads data, trains the model, and saves all artifacts.
"""
import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
from pathlib import Path
import argparse
import logging
import warnings

warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_data(data_paths):
    """Load and combine data from multiple CSV files."""
    dfs = []
    
    for path in data_paths:
        if Path(path).exists():
            # Try different encodings
            encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(path, encoding=encoding)
                    logger.info(f"Loaded {len(df)} samples from {path} using {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                logger.error(f"Could not read {path} with any encoding")
                continue
                
            dfs.append(df)
        else:
            logger.warning(f"File not found: {path}")
    
    if not dfs:
        raise ValueError("No valid data files found")
    
    # Combine all dataframes
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Remove duplicates based on all features except username
    feature_cols = [col for col in combined_df.columns if col not in ['username', 'is_fake']]
    combined_df = combined_df.drop_duplicates(subset=feature_cols, keep='first')
    
    logger.info(f"Combined dataset: {len(combined_df)} samples after removing duplicates")
    
    return combined_df


def preprocess_data(df):
    """Preprocess the data for training.""" 
    logger.info("Preprocessing data...")
    
    # Create column mapping for different dataset formats
    column_mapping = {
        'profile pic': 'has_profile_pic',
        'nums/length username': 'username_numeric_ratio',
        'fullname words': 'fullname_words',
        'nums/length fullname': 'fullname_numeric_ratio', 
        'name==username': 'name_equals_username',
        'description length': 'bio_length',
        'external URL': 'has_external_url',
        'private': 'is_private',
        '#posts': 'post_count',
        '#followers': 'follower_count',
        '#follows': 'following_count',
        'fake': 'is_fake'
    }
    
    # Rename columns if needed
    df_renamed = df.rename(columns=column_mapping)
    
    # Skip Instagram analytics data (has different structure)
    if 'Impressions' in df.columns:
        logger.warning("Skipping Instagram analytics data - not account classification data")
        return None, None, None
    
    # Define the features we'll use
    required_features = ['has_profile_pic', 'bio_length', 'has_external_url', 'is_private', 
                        'post_count', 'follower_count', 'following_count', 'is_fake']
    
    # Check if we have the minimum required columns
    missing_cols = set(required_features) - set(df_renamed.columns)
    if missing_cols:
        logger.error(f"Missing required columns: {missing_cols}")
        return None, None, None
    
    # Create a clean dataframe with our features
    df_clean = df_renamed[required_features].copy()
    
    # Handle missing values
    df_clean = df_clean.fillna(0)
    
    # Add synthetic features that might be missing
    df_clean['avg_likes_per_post'] = np.random.exponential(scale=10, size=len(df_clean))  # Synthetic
    df_clean['avg_comments_per_post'] = df_clean['avg_likes_per_post'] * np.random.uniform(0.01, 0.1, size=len(df_clean))
    
    # Calculate derived features
    df_clean['follower_following_ratio'] = df_clean['follower_count'] / df_clean['following_count'].replace(0, 1)
    df_clean['engagement_rate'] = ((df_clean['avg_likes_per_post'] + df_clean['avg_comments_per_post']) / 
                                   df_clean['follower_count'].replace(0, 1)) * 100
    
    # Cap extreme values
    df_clean['follower_following_ratio'] = df_clean['follower_following_ratio'].clip(upper=1000)
    df_clean['engagement_rate'] = df_clean['engagement_rate'].clip(upper=500)
    
    # Final feature columns for model
    feature_columns = [
        'follower_count', 'following_count', 'post_count', 'bio_length',
        'has_profile_pic', 'has_external_url', 'avg_likes_per_post',
        'avg_comments_per_post', 'is_private', 'follower_following_ratio', 'engagement_rate'
    ]
    
    X = df_clean[feature_columns]
    y = df_clean['is_fake']
    
    logger.info(f"Preprocessed {len(X)} samples with {len(feature_columns)} features")
    
    return X, y, feature_columns


def train_model(X_train, y_train, X_test, y_test):
    """Train XGBoost model with optimized hyperparameters."""
    logger.info("Training XGBoost model...")
    
    # Calculate class weights for imbalanced data
    class_counts = np.bincount(y_train)
    total_samples = len(y_train)
    scale_pos_weight = class_counts[0] / class_counts[1] if class_counts[1] > 0 else 1.0
    
    logger.info(f"Class distribution - Real: {class_counts[0]}, Fake: {class_counts[1]}")
    logger.info(f"Scale pos weight: {scale_pos_weight:.2f}")
    
    # Initialize XGBoost classifier with optimized parameters
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        eval_metric='logloss',
        use_label_encoder=False
    )
    
    # Train the model
    model.fit(
        X_train, 
        y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )
    
    logger.info("Model training completed")
    
    return model


def evaluate_model(model, X_test, y_test):
    """Evaluate the trained model."""
    logger.info("Evaluating model...")
    
    # Make predictions
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    
    # Print evaluation results
    print(f"\n{'='*50}")
    print(f"MODEL EVALUATION RESULTS")
    print(f"{'='*50}")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print(f"{'='*50}")
    
    # Detailed classification report
    print(f"\nDetailed Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Real', 'Fake']))
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix:")
    print(f"              Predicted")
    print(f"Actual    Real    Fake")
    print(f"Real      {cm[0,0]:4d}    {cm[0,1]:4d}")
    print(f"Fake      {cm[1,0]:4d}    {cm[1,1]:4d}")
    
    # Feature importance
    feature_importance = model.feature_importances_
    feature_names = model.get_booster().feature_names
    
    print(f"\nTop 10 Most Important Features:")
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': feature_importance
    }).sort_values('importance', ascending=False)
    
    for i, row in importance_df.head(10).iterrows():
        print(f"{str(row['feature']):25s}: {row['importance']:.4f}")
    
    return {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'feature_importance': importance_df
    }


def save_model_artifacts(model, scaler, feature_names, output_dir):
    """Save all model artifacts."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Save XGBoost model
    model_path = output_dir / 'instagram_model.json'
    model.save_model(str(model_path))
    logger.info(f"Saved XGBoost model to {model_path}")
    
    # Save scaler
    scaler_path = output_dir / 'scaler.pkl'
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    logger.info(f"Saved scaler to {scaler_path}")
    
    # Save feature names
    feature_names_path = output_dir / 'feature_names.pkl'
    with open(feature_names_path, 'wb') as f:
        pickle.dump(feature_names, f)
    logger.info(f"Saved feature names to {feature_names_path}")
    
    logger.info(f"All model artifacts saved to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Train Instagram fake account detection model')
    parser.add_argument('--data-files', nargs='+', required=True, 
                       help='Paths to CSV data files')
    parser.add_argument('--output-dir', default='ml_model',
                       help='Directory to save model artifacts')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Test set size (default: 0.2)')
    parser.add_argument('--random-state', type=int, default=42,
                       help='Random state for reproducibility')
    
    args = parser.parse_args()
    
    try:
        # Load data
        logger.info("Starting model training pipeline...")
        df = load_data(args.data_files)
        
        # Preprocess data
        X, y, feature_names = preprocess_data(df)
        
        if X is None:
            logger.error("No valid data found after preprocessing")
            return
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=args.test_size, 
            random_state=args.random_state,
            stratify=y
        )
        
        logger.info(f"Train set: {len(X_train)} samples")
        logger.info(f"Test set: {len(X_test)} samples")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = train_model(X_train_scaled, y_train, X_test_scaled, y_test)
        
        # Evaluate model
        metrics = evaluate_model(model, X_test_scaled, y_test)
        
        # Save model artifacts
        save_model_artifacts(model, scaler, feature_names, args.output_dir)
        
        print(f"\n{'='*50}")
        print(f"TRAINING COMPLETED SUCCESSFULLY!")
        print(f"Model artifacts saved to: {args.output_dir}")
        print(f"Final accuracy: {metrics['accuracy']:.4f}")
        print(f"{'='*50}")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
