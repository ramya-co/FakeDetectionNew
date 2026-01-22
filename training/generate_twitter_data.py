"""
Generate synthetic training datasets for Twitter fake account detection.
This creates a dataset with similar structure to Instagram data but adapted for Twitter.
"""
import pandas as pd
import numpy as np
import random
from pathlib import Path

# Set random seeds for reproducibility
np.random.seed(42)
random.seed(42)

def generate_twitter_dataset(n_samples=10000):
    """
    Generate synthetic Twitter account data for fake account detection.
    
    Features match the Instagram structure:
    - follower_count, following_count, post_count (tweets)
    - bio_length, has_profile_pic, has_external_url
    - avg_likes_per_post, avg_comments_per_post (replies + retweets)
    - is_private
    - Label: 0 = Real, 1 = Fake
    """
    
    data = []
    
    # Generate half real, half fake accounts
    n_real = n_samples // 2
    n_fake = n_samples - n_real
    
    # Generate REAL accounts
    for i in range(n_real):
        # Real accounts typically have:
        # - Balanced follower/following ratios
        # - Consistent posting history
        # - Decent engagement
        # - Complete profiles
        
        follower_count = np.random.lognormal(6, 2)  # Mean ~400, varies widely
        follower_count = max(10, int(follower_count))
        
        # Real accounts have reasonable following counts
        if follower_count < 100:
            following_count = np.random.randint(50, 500)
        elif follower_count < 1000:
            following_count = np.random.randint(100, 800)
        else:
            following_count = np.random.randint(100, 2000)
        
        post_count = np.random.randint(50, 10000)
        bio_length = np.random.randint(20, 160)  # Twitter has 160 char limit
        has_profile_pic = 1 if random.random() > 0.05 else 0  # 95% have profile pic
        has_external_url = 1 if random.random() > 0.4 else 0  # 60% have URL
        
        # Engagement based on follower count
        engagement_factor = np.random.uniform(0.01, 0.05)  # 1-5% engagement
        avg_likes_per_post = max(1, int(follower_count * engagement_factor * np.random.uniform(0.5, 2)))
        avg_comments_per_post = max(0, int(avg_likes_per_post * np.random.uniform(0.05, 0.2)))
        
        is_private = 1 if random.random() > 0.85 else 0  # 15% private
        
        data.append({
            'follower_count': follower_count,
            'following_count': following_count,
            'post_count': post_count,
            'bio_length': bio_length,
            'has_profile_pic': has_profile_pic,
            'has_external_url': has_external_url,
            'avg_likes_per_post': avg_likes_per_post,
            'avg_comments_per_post': avg_comments_per_post,
            'is_private': is_private,
            'fake': 0
        })
    
    # Generate FAKE accounts
    for i in range(n_fake):
        # Fake accounts typically have:
        # - High follower/low engagement OR low follower/high following
        # - Sparse posting OR spam posting
        # - Incomplete profiles
        # - Suspicious metrics
        
        fake_type = random.choice(['bot', 'bought_followers', 'spam', 'inactive'])
        
        if fake_type == 'bot':
            # Bot accounts: low followers, high following, few posts, no engagement
            follower_count = np.random.randint(0, 100)
            following_count = np.random.randint(500, 5000)
            post_count = np.random.randint(0, 50)
            bio_length = np.random.randint(0, 50)
            has_profile_pic = 1 if random.random() > 0.5 else 0
            has_external_url = 1 if random.random() > 0.7 else 0
            avg_likes_per_post = np.random.uniform(0, 2)
            avg_comments_per_post = np.random.uniform(0, 0.5)
            is_private = 0
            
        elif fake_type == 'bought_followers':
            # Bought followers: high followers, low engagement
            follower_count = np.random.randint(1000, 50000)
            following_count = np.random.randint(50, 500)
            post_count = np.random.randint(5, 200)
            bio_length = np.random.randint(10, 100)
            has_profile_pic = 1
            has_external_url = 1 if random.random() > 0.3 else 0
            # Very low engagement relative to followers
            avg_likes_per_post = np.random.uniform(5, 100)  # Should be much higher
            avg_comments_per_post = np.random.uniform(0, 10)
            is_private = 0
            
        elif fake_type == 'spam':
            # Spam accounts: high posting, low followers, promotional content
            follower_count = np.random.randint(10, 500)
            following_count = np.random.randint(1000, 5000)
            post_count = np.random.randint(1000, 50000)
            bio_length = np.random.randint(50, 160)  # Often has spammy bio
            has_profile_pic = 1 if random.random() > 0.3 else 0
            has_external_url = 1 if random.random() > 0.2 else 0  # 80% have URL (spam links)
            avg_likes_per_post = np.random.uniform(0, 5)
            avg_comments_per_post = np.random.uniform(0, 2)
            is_private = 0
            
        else:  # inactive
            # Inactive/abandoned fake accounts
            follower_count = np.random.randint(0, 200)
            following_count = np.random.randint(0, 100)
            post_count = np.random.randint(0, 20)
            bio_length = np.random.randint(0, 30)
            has_profile_pic = 1 if random.random() > 0.6 else 0
            has_external_url = 0
            avg_likes_per_post = 0
            avg_comments_per_post = 0
            is_private = 0
        
        data.append({
            'follower_count': int(follower_count),
            'following_count': int(following_count),
            'post_count': int(post_count),
            'bio_length': int(bio_length),
            'has_profile_pic': int(has_profile_pic),
            'has_external_url': int(has_external_url),
            'avg_likes_per_post': float(avg_likes_per_post),
            'avg_comments_per_post': float(avg_comments_per_post),
            'is_private': int(is_private),
            'fake': 1
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    return df

if __name__ == '__main__':
    # Create datasets directory if it doesn't exist
    datasets_dir = Path(__file__).parent / 'datasets'
    datasets_dir.mkdir(exist_ok=True)
    
    # Generate Twitter dataset
    print("Generating Twitter synthetic dataset...")
    twitter_df = generate_twitter_dataset(n_samples=10000)
    
    # Save to CSV
    output_path = datasets_dir / 'twitter_data.csv'
    twitter_df.to_csv(output_path, index=False)
    print(f"✅ Twitter dataset saved to: {output_path}")
    
    # Print statistics
    print("\n📊 Dataset Statistics:")
    print(f"Total samples: {len(twitter_df)}")
    print(f"Real accounts: {(twitter_df['fake'] == 0).sum()}")
    print(f"Fake accounts: {(twitter_df['fake'] == 1).sum()}")
    print("\nFeature statistics:")
    print(twitter_df.describe())
    
    # Print class distribution
    print("\n🎯 Class Distribution:")
    print(twitter_df['fake'].value_counts())
