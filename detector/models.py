"""
Django models for Instagram fake account detection.
"""
from django.db import models
from django.utils import timezone
import json


class AnalysisHistory(models.Model):
    """Model to store analysis history for Instagram accounts."""
    
    # Input method choices
    INPUT_METHOD_CHOICES = [
        ('manual', 'Manual Input'),
        ('scraped', 'URL Scraping'),
    ]
    
    # Prediction choices
    PREDICTION_CHOICES = [
        ('Real', 'Real Account'),
        ('Fake', 'Fake Account'),
    ]
    
    # Basic info
    username = models.CharField(max_length=255, help_text="Instagram username")
    input_method = models.CharField(
        max_length=10, 
        choices=INPUT_METHOD_CHOICES,
        help_text="How the data was collected"
    )
    
    # Account features
    follower_count = models.IntegerField(help_text="Number of followers")
    following_count = models.IntegerField(help_text="Number of following")
    post_count = models.IntegerField(help_text="Number of posts")
    bio_length = models.IntegerField(help_text="Length of bio text")
    has_profile_pic = models.BooleanField(help_text="Has profile picture")
    has_external_url = models.BooleanField(help_text="Has external URL in bio")
    avg_likes_per_post = models.FloatField(help_text="Average likes per post")
    avg_comments_per_post = models.FloatField(help_text="Average comments per post")
    
    # Calculated features (stored for reference)
    follower_following_ratio = models.FloatField(help_text="Follower to following ratio")
    engagement_rate = models.FloatField(help_text="Engagement rate percentage")
    is_private = models.BooleanField(default=False, help_text="Is account private")
    
    # Prediction results
    prediction = models.CharField(
        max_length=10,
        choices=PREDICTION_CHOICES,
        help_text="Model prediction result"
    )
    confidence_score = models.FloatField(help_text="Prediction confidence (0-1)")
    
    # SHAP explanation (stored as JSON)
    shap_explanation = models.JSONField(
        help_text="Top features influencing prediction",
        default=dict
    )
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Analysis History"
        verbose_name_plural = "Analysis Histories"
    
    def __str__(self):
        return f"{self.username} - {self.prediction} ({self.confidence_score:.2%})"
    
    def get_top_shap_features(self, limit=5):
        """Get top SHAP features influencing the prediction."""
        if self.shap_explanation and isinstance(self.shap_explanation, dict):
            features = self.shap_explanation.get('top_features', [])
            return features[:limit]
        return []
    
    def save(self, *args, **kwargs):
        """Override save to ensure data consistency."""
        # Calculate derived features if not set
        if self.follower_count and self.following_count:
            if self.following_count > 0:
                self.follower_following_ratio = self.follower_count / self.following_count
            else:
                self.follower_following_ratio = float('inf')
        
        if self.follower_count and self.avg_likes_per_post is not None and self.avg_comments_per_post is not None:
            if self.follower_count > 0:
                self.engagement_rate = ((self.avg_likes_per_post + self.avg_comments_per_post) / self.follower_count) * 100
            else:
                self.engagement_rate = 0.0
        
        super().save(*args, **kwargs)


# SIMULATION MODELS FOR INSTAGRAM CLONE

class SimulatedUser(models.Model):
    """Model for users in the Instagram simulation"""
    username = models.CharField(max_length=150, unique=True)
    bio = models.TextField(blank=True, max_length=2200)
    profile_picture = models.ImageField(upload_to='simulation/profiles/', blank=True, null=True)
    external_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_bot = models.BooleanField(default=False)  # For pre-populated fake users
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.username
    
    @property
    def session_duration_minutes(self):
        """Calculate session duration in minutes"""
        if self.session_end:
            duration = (self.session_end - self.session_start).total_seconds()
        else:
            duration = (timezone.now() - self.session_start).total_seconds()
        return round(duration / 60, 2)


class SimulatedPost(models.Model):
    """Model for posts in the simulation"""
    user = models.ForeignKey(SimulatedUser, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='simulation/posts/')
    caption = models.TextField(blank=True, max_length=2200)
    location = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s post - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def update_likes_count(self):
        """Update the likes count from actual likes"""
        self.likes_count = self.likes.count()
        self.save(update_fields=['likes_count'])
    
    @property
    def comments_count(self):
        """Get the count of comments for this post"""
        return self.comments.count()


class SimulatedLike(models.Model):
    """Model for likes in the simulation"""
    user = models.ForeignKey(SimulatedUser, on_delete=models.CASCADE, related_name='likes_given')
    post = models.ForeignKey(SimulatedPost, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'post')  # Prevent duplicate likes
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} liked {self.post.user.username}'s post"


class SimulatedComment(models.Model):
    """Model for comments in the simulation"""
    user = models.ForeignKey(SimulatedUser, on_delete=models.CASCADE, related_name='comments_given')
    post = models.ForeignKey(SimulatedPost, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=2200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} commented on {self.post.user.username}'s post"


class SimulatedActivity(models.Model):
    """Model tracking all activity metrics for ML analysis"""
    user = models.OneToOneField(SimulatedUser, on_delete=models.CASCADE, related_name='activity')
    total_posts = models.IntegerField(default=0)
    total_likes_given = models.IntegerField(default=0)
    total_comments_given = models.IntegerField(default=0)
    average_post_interval = models.FloatField(default=0.0)  # seconds between posts
    average_like_interval = models.FloatField(default=0.0)  # seconds between likes
    session_duration = models.FloatField(default=0.0)  # total seconds in simulation
    bio_length = models.IntegerField(default=0)
    has_profile_pic = models.BooleanField(default=False)
    has_external_url = models.BooleanField(default=False)
    username_entropy = models.FloatField(default=0.0)  # measure of username randomness
    avg_comment_length = models.FloatField(default=0.0)
    engagement_rate = models.FloatField(default=0.0)
    calculated_follower_count = models.IntegerField(default=0)  # simulated based on activity
    calculated_following_count = models.IntegerField(default=0)  # simulated based on activity
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s activity"
    
    def update_metrics(self):
        """Update all activity metrics"""
        from django.db.models import Avg
        import math
        
        # Update basic counts
        self.total_posts = self.user.posts.count()
        self.total_likes_given = self.user.likes_given.count()
        self.total_comments_given = self.user.comments_given.count()
        
        # Update profile metrics
        self.bio_length = len(self.user.bio)
        self.has_profile_pic = bool(self.user.profile_picture)
        self.has_external_url = bool(self.user.external_url)
        
        # Calculate username entropy (randomness measure)
        username = self.user.username.lower()
        if username:
            # Simple entropy calculation
            char_counts = {}
            for char in username:
                char_counts[char] = char_counts.get(char, 0) + 1
            
            entropy = 0
            username_length = len(username)
            for count in char_counts.values():
                probability = count / username_length
                if probability > 0:
                    entropy -= probability * math.log2(probability)
            
            self.username_entropy = entropy
        
        # Calculate average comment length
        comments = self.user.comments_given.all()
        if comments:
            avg_length = comments.aggregate(avg_len=Avg('text'))['avg_len'] or 0
            self.avg_comment_length = round(avg_length, 2)
        
        # Calculate posting intervals
        posts = list(self.user.posts.order_by('created_at'))
        if len(posts) > 1:
            intervals = []
            for i in range(1, len(posts)):
                interval = (posts[i].created_at - posts[i-1].created_at).total_seconds()
                intervals.append(interval)
            self.average_post_interval = sum(intervals) / len(intervals)
        
        # Calculate liking intervals
        likes = list(self.user.likes_given.order_by('created_at'))
        if len(likes) > 1:
            intervals = []
            for i in range(1, len(likes)):
                interval = (likes[i].created_at - likes[i-1].created_at).total_seconds()
                intervals.append(interval)
            self.average_like_interval = sum(intervals) / len(intervals)
        
        # Calculate session duration
        self.session_duration = self.user.session_duration_minutes * 60
        
        # Simulate follower/following counts based on activity
        # More active users get more followers (simplified simulation)
        activity_score = (self.total_posts * 10) + (self.total_likes_given * 2) + (self.total_comments_given * 5)
        base_followers = max(50, activity_score + (self.total_posts * 100))
        self.calculated_follower_count = min(10000, base_followers)
        
        base_following = max(20, activity_score // 10 + 100)
        self.calculated_following_count = min(2000, base_following)
        
        # Calculate engagement rate
        if self.total_posts > 0:
            total_engagement = 0
            for post in self.user.posts.all():
                post_engagement = post.likes_count + post.comments.count()
                total_engagement += post_engagement
            
            avg_engagement_per_post = total_engagement / self.total_posts
            if self.calculated_follower_count > 0:
                self.engagement_rate = (avg_engagement_per_post / self.calculated_follower_count) * 100
            else:
                self.engagement_rate = 0.0
        
        self.save()
    
    def meets_analysis_threshold(self):
        """Check if user has enough activity for analysis"""
        return (
            self.total_posts >= 1 or 
            self.total_likes_given >= 5 or 
            self.total_comments_given >= 3 or
            self.session_duration >= 120  # 2 minutes
        )


class SimulatedPrediction(models.Model):
    """Model storing all predictions for simulated users"""
    PREDICTION_CHOICES = [
        ('Real', 'Real Account'),
        ('Fake', 'Fake Account'),
    ]
    
    user = models.ForeignKey(SimulatedUser, on_delete=models.CASCADE, related_name='predictions')
    prediction = models.CharField(max_length=10, choices=PREDICTION_CHOICES)
    confidence_score = models.FloatField()  # 0-1 probability
    predicted_at = models.DateTimeField(auto_now_add=True)
    features_snapshot = models.JSONField()  # store all features used for this prediction
    shap_values = models.JSONField()  # store SHAP explanation as JSON
    top_features = models.JSONField()  # store top 5 features with their SHAP values
    is_latest = models.BooleanField(default=True)  # mark the most recent prediction
    
    class Meta:
        ordering = ['-predicted_at']
        indexes = [
            models.Index(fields=['user', 'is_latest']),
            models.Index(fields=['predicted_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.prediction} ({self.confidence_score:.2%})"
    
    def save(self, *args, **kwargs):
        # Set all other predictions for this user to not latest
        if self.is_latest:
            SimulatedPrediction.objects.filter(user=self.user).update(is_latest=False)
        super().save(*args, **kwargs)
    
    @property
    def confidence_percentage(self):
        """Return confidence as percentage"""
        return self.confidence_score * 100
    
    @property
    def risk_level(self):
        """Determine risk level based on prediction and confidence"""
        if self.prediction == 'Fake':
            if self.confidence_score >= 0.8:
                return 'High Risk'
            elif self.confidence_score >= 0.6:
                return 'Medium Risk'
            else:
                return 'Low Risk'
        else:  # Real
            if self.confidence_score >= 0.8:
                return 'Very Likely Real'
            elif self.confidence_score >= 0.6:
                return 'Likely Real'
            else:
                return 'Uncertain'
