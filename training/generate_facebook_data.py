"""
Generate synthetic training datasets for Facebook fake account detection.
This creates a dataset with similar structure to Instagram data but adapted for Facebook.
"""
import pandas as pd
import numpy as np
import random
from pathlib import Path

# Set random seeds for reproducibility
np.random.seed(43)
random.seed(43)

def generate_facebook_dataset(n_samples=10000):
    """
    Generate synthetic Facebook account data for fake account detection.
    
    Features match the Instagram structure:
    - follower_count (friends/followers), following_count
    - post_count, bio_length, has_profile_pic, has_external_url
    - avg_likes_per_post, avg_comments_per_post
    - is_private
    - Label: 0 = Real, 1 = Fake
    """
    
    data = []
    
    # Generate half real, half fake accounts
    n_real = n_samples // 2
    n_fake = n_samples - n_real
    
    # Generate REAL accounts
    for i in range(n_real):
        # Real Facebook accounts typically have:
        # - Friend counts between 50-5000 (5000 is the friend limit)
        # - Regular posting activity
        # - Good engagement from actual friends
        # - Complete profiles with photos and info
        
        # Facebook friend count (max 5000 for personal profiles)
        follower_count = min(5000, max(20, int(np.random.lognormal(5.5, 1.5))))
        
        # Following (pages, public figures) - less common on personal profiles
        following_count = np.random.randint(0, 300)
        
        post_count = np.random.randint(20, 2000)
        bio_length = np.random.randint(50, 300)  # Facebook bios can be longer
        has_profile_pic = 1 if random.random() > 0.02 else 0  # 98% have profile pic
        has_external_url = 1 if random.random() > 0.7 else 0  # 30% have website
        
        # Facebook typically has higher engagement among friends
        engagement_factor = np.random.uniform(0.02, 0.15)  # 2-15% of friends engage
        avg_likes_per_post = max(1, int(follower_count * engagement_factor * np.random.uniform(0.5, 2)))
        avg_comments_per_post = max(1, int(avg_likes_per_post * np.random.uniform(0.1, 0.4)))
        
        is_private = 1 if random.random() > 0.5 else 0  # About 50% private on Facebook
        
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
        # Fake Facebook accounts typically:
        # - Clone/impersonation accounts
        # - Spam/bot accounts
        # - Catfish/romance scam accounts
        # - Business spam accounts
        
        fake_type = random.choice(['clone', 'bot', 'catfish', 'spam'])
        
        if fake_type == 'clone':
            # Clone/impersonation accounts: new account pretending to be someone
            follower_count = np.random.randint(0, 150)  # Few friends initially
            following_count = np.random.randint(100, 1000)  # Sends many friend requests
            post_count = np.random.randint(0, 50)  # Few or no posts
            bio_length = np.random.randint(20, 200)  # Copies bio from real account
            has_profile_pic = 1 if random.random() > 0.2 else 0  # Usually has pic (stolen)
            has_external_url = 1 if random.random() > 0.8 else 0
            avg_likes_per_post = np.random.uniform(0, 5)
            avg_comments_per_post = np.random.uniform(0, 2)
            is_private = 0  # Usually public to seem legitimate
            
        elif fake_type == 'bot':
            # Bot accounts: automated fake profiles
            follower_count = np.random.randint(0, 50)
            following_count = np.random.randint(500, 5000)
            post_count = np.random.randint(0, 30)
            bio_length = np.random.randint(0, 50)
            has_profile_pic = 1 if random.random() > 0.6 else 0
            has_external_url = 1 if random.random() > 0.5 else 0
            avg_likes_per_post = np.random.uniform(0, 1)
            avg_comments_per_post = np.random.uniform(0, 0.5)
            is_private = 0
            
        elif fake_type == 'catfish':
            # Catfish/romance scam accounts: fake identity for manipulation
            follower_count = np.random.randint(100, 1000)
            following_count = np.random.randint(200, 2000)
            post_count = np.random.randint(10, 200)
            bio_length = np.random.randint(100, 300)  # Elaborate fake backstory
            has_profile_pic = 1  # Always has attractive stolen photos
            has_external_url = 1 if random.random() > 0.6 else 0
            # Low engagement despite having friends
            avg_likes_per_post = np.random.uniform(2, 20)
            avg_comments_per_post = np.random.uniform(0, 5)
            is_private = 0  # Public to attract victims
            
        else:  # spam
            # Business spam accounts
            follower_count = np.random.randint(50, 500)
            following_count = np.random.randint(1000, 5000)
            post_count = np.random.randint(100, 5000)  # Lots of spam posts
            bio_length = np.random.randint(50, 300)
            has_profile_pic = 1
            has_external_url = 1 if random.random() > 0.1 else 0  # 90% have spam links
            avg_likes_per_post = np.random.uniform(1, 10)
            avg_comments_per_post = np.random.uniform(0, 3)
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
    df = df.sample(frac=1, random_state=43).reset_index(drop=True)
    
    return df

if __name__ == '__main__':
    # Create datasets directory if it doesn't exist
    datasets_dir = Path(__file__).parent / 'datasets'
    datasets_dir.mkdir(exist_ok=True)
    
    # Generate Facebook dataset
    print("Generating Facebook synthetic dataset...")
    facebook_df = generate_facebook_dataset(n_samples=10000)
    
    # Save to CSV
    output_path = datasets_dir / 'facebook_data.csv'
    facebook_df.to_csv(output_path, index=False)
    print(f"✅ Facebook dataset saved to: {output_path}")
    
    # Print statistics
    print("\n📊 Dataset Statistics:")
    print(f"Total samples: {len(facebook_df)}")
    print(f"Real accounts: {(facebook_df['fake'] == 0).sum()}")
    print(f"Fake accounts: {(facebook_df['fake'] == 1).sum()}")
    print("\nFeature statistics:")
    print(facebook_df.describe())
    
    # Print class distribution
    print("\n🎯 Class Distribution:")
    print(facebook_df['fake'].value_counts())
