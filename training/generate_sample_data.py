"""
Generate synthetic Instagram account data for training.
This script creates realistic fake and real account data for model training.
"""
import pandas as pd
import numpy as np
import random
from pathlib import Path
import argparse


def generate_real_accounts(n_samples=1000):
    """Generate realistic real Instagram account data."""
    data = []
    
    for i in range(n_samples):
        # Real accounts tend to have more balanced metrics
        follower_count = np.random.choice([
            np.random.randint(100, 1000),      # Small accounts (40%)
            np.random.randint(1000, 10000),    # Medium accounts (35%)
            np.random.randint(10000, 100000),  # Large accounts (20%)
            np.random.randint(100000, 1000000) # Very large accounts (5%)
        ], p=[0.4, 0.35, 0.2, 0.05])
        
        # Following count is usually reasonable for real accounts
        following_count = np.random.randint(50, min(follower_count + 500, 2000))
        
        # Post count varies but is usually reasonable
        post_count = np.random.randint(10, 2000)
        
        # Bio length varies but real accounts often have descriptive bios
        bio_length = np.random.choice([
            np.random.randint(0, 50),      # Short or no bio (30%)
            np.random.randint(50, 150),    # Medium bio (50%)
            np.random.randint(150, 300)    # Long bio (20%)
        ], p=[0.3, 0.5, 0.2])
        
        # Real accounts usually have profile pictures
        has_profile_pic = np.random.choice([True, False], p=[0.9, 0.1])
        
        # External URLs are common but not universal
        has_external_url = np.random.choice([True, False], p=[0.4, 0.6])
        
        # Engagement rates are typically reasonable for real accounts
        base_engagement = max(0.1, np.random.normal(2.0, 1.5))  # 2% average engagement
        
        if post_count > 0:
            avg_likes_per_post = max(1, follower_count * (base_engagement / 100) * np.random.uniform(0.5, 2.0))
            avg_comments_per_post = max(0, avg_likes_per_post * np.random.uniform(0.02, 0.15))
        else:
            avg_likes_per_post = 0
            avg_comments_per_post = 0
        
        # Private accounts
        is_private = np.random.choice([True, False], p=[0.3, 0.7])
        
        data.append({
            'username': f'real_user_{i+1}',
            'follower_count': follower_count,
            'following_count': following_count,
            'post_count': post_count,
            'bio_length': bio_length,
            'has_profile_pic': int(has_profile_pic),
            'has_external_url': int(has_external_url),
            'avg_likes_per_post': avg_likes_per_post,
            'avg_comments_per_post': avg_comments_per_post,
            'follower_following_ratio': follower_count / max(following_count, 1),
            'engagement_rate': ((avg_likes_per_post + avg_comments_per_post) / max(follower_count, 1)) * 100,
            'is_private': int(is_private),
            'is_fake': 0  # Real account
        })
    
    return data


def generate_fake_accounts(n_samples=1000):
    """Generate realistic fake Instagram account data."""
    data = []
    
    for i in range(n_samples):
        # Fake accounts often have suspicious follower patterns
        fake_type = np.random.choice(['bot_farm', 'purchased_followers', 'engagement_pods'], p=[0.4, 0.4, 0.2])
        
        if fake_type == 'bot_farm':
            # Bot farms: many followers, few following, low engagement
            follower_count = np.random.randint(10000, 500000)
            following_count = np.random.randint(0, 100)
            avg_likes_per_post = max(1, follower_count * np.random.uniform(0.001, 0.01))  # Very low engagement
            avg_comments_per_post = max(0, avg_likes_per_post * np.random.uniform(0.001, 0.02))
            
        elif fake_type == 'purchased_followers':
            # Purchased followers: high followers, normal following, suspicious engagement
            follower_count = np.random.randint(5000, 100000)
            following_count = np.random.randint(200, 2000)
            # Engagement doesn't match follower count
            avg_likes_per_post = max(1, np.random.randint(50, 500))  # Fixed low engagement
            avg_comments_per_post = max(0, avg_likes_per_post * np.random.uniform(0.001, 0.05))
            
        else:  # engagement_pods
            # Engagement pods: artificial high engagement, suspicious ratios
            follower_count = np.random.randint(1000, 20000)
            following_count = np.random.randint(500, 3000)
            # Artificially high engagement
            avg_likes_per_post = max(1, follower_count * np.random.uniform(0.05, 0.3))
            avg_comments_per_post = max(0, avg_likes_per_post * np.random.uniform(0.1, 0.4))
        
        # Post count varies but fake accounts might have few posts
        post_count = np.random.choice([
            np.random.randint(0, 10),      # Very few posts (30%)
            np.random.randint(10, 50),     # Few posts (40%)
            np.random.randint(50, 500)     # Normal posts (30%)
        ], p=[0.3, 0.4, 0.3])
        
        # Bio characteristics
        bio_length = np.random.choice([
            0,                             # No bio (40%)
            np.random.randint(1, 30),      # Very short bio (35%)
            np.random.randint(30, 100)     # Short bio (25%)
        ], p=[0.4, 0.35, 0.25])
        
        # Fake accounts less likely to have profile pictures
        has_profile_pic = np.random.choice([True, False], p=[0.6, 0.4])
        
        # External URLs less common
        has_external_url = np.random.choice([True, False], p=[0.2, 0.8])
        
        # Private accounts less common for fake accounts
        is_private = np.random.choice([True, False], p=[0.1, 0.9])
        
        data.append({
            'username': f'fake_user_{i+1}',
            'follower_count': follower_count,
            'following_count': following_count,
            'post_count': post_count,
            'bio_length': bio_length,
            'has_profile_pic': int(has_profile_pic),
            'has_external_url': int(has_external_url),
            'avg_likes_per_post': avg_likes_per_post,
            'avg_comments_per_post': avg_comments_per_post,
            'follower_following_ratio': follower_count / max(following_count, 1),
            'engagement_rate': ((avg_likes_per_post + avg_comments_per_post) / max(follower_count, 1)) * 100,
            'is_private': int(is_private),
            'is_fake': 1  # Fake account
        })
    
    return data


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic Instagram account data')
    parser.add_argument('--real-samples', type=int, default=1000, help='Number of real account samples')
    parser.add_argument('--fake-samples', type=int, default=1000, help='Number of fake account samples')
    parser.add_argument('--output-dir', type=str, default='datasets', help='Output directory')
    parser.add_argument('--split', action='store_true', help='Split into multiple files')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print(f"Generating {args.real_samples} real accounts and {args.fake_samples} fake accounts...")
    
    # Generate data
    real_data = generate_real_accounts(args.real_samples)
    fake_data = generate_fake_accounts(args.fake_samples)
    
    # Combine data
    all_data = real_data + fake_data
    
    # Shuffle data
    random.shuffle(all_data)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    if args.split:
        # Split into 3 files
        n_total = len(df)
        n_per_file = n_total // 3
        
        df1 = df.iloc[:n_per_file]
        df2 = df.iloc[n_per_file:2*n_per_file]
        df3 = df.iloc[2*n_per_file:]
        
        # Save files
        df1.to_csv(output_dir / 'dataset1.csv', index=False)
        df2.to_csv(output_dir / 'dataset2.csv', index=False)
        df3.to_csv(output_dir / 'dataset3.csv', index=False)
        
        print(f"Saved 3 dataset files to {output_dir}/")
        print(f"Dataset 1: {len(df1)} samples")
        print(f"Dataset 2: {len(df2)} samples")
        print(f"Dataset 3: {len(df3)} samples")
    else:
        # Save as single file
        df.to_csv(output_dir / 'instagram_data.csv', index=False)
        print(f"Saved dataset to {output_dir}/instagram_data.csv")
    
    # Print statistics
    print(f"\nDataset Statistics:")
    print(f"Total samples: {len(df)}")
    print(f"Real accounts: {len(df[df['is_fake'] == 0])}")
    print(f"Fake accounts: {len(df[df['is_fake'] == 1])}")
    print(f"Features: {len(df.columns) - 1}")  # Exclude target column
    
    # Print feature statistics
    print(f"\nFeature Statistics:")
    for col in df.columns:
        if col not in ['username', 'is_fake']:
            print(f"{col}: mean={df[col].mean():.2f}, std={df[col].std():.2f}")


if __name__ == "__main__":
    main()
