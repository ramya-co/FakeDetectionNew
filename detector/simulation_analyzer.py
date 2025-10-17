"""
Automatic prediction system for Instagram simulation.
This module handles real-time analysis of simulated user behavior.
"""
import logging
from django.utils import timezone
from detector.models import SimulatedUser, SimulatedPost, SimulatedLike, SimulatedComment, SimulatedActivity, SimulatedPrediction
from .predictor import InstagramPredictor

logger = logging.getLogger(__name__)


class SimulationAnalyzer:
    """
    Handles automatic prediction and analysis of simulated user behavior.
    """
    
    def __init__(self):
        self.predictor = InstagramPredictor()
        # Load the model during initialization
        try:
            self.predictor.load_model()
            logger.info("ML model loaded successfully in SimulationAnalyzer")
        except Exception as e:
            logger.error(f"Failed to load ML model in SimulationAnalyzer: {str(e)}")
    
    def check_and_predict(self, user_id):
        """
        Check if user meets threshold and run prediction if ready.
        Called after each user action (post, like, comment).
        """
        try:
            user = SimulatedUser.objects.get(id=user_id)
            
            # Get or create activity record
            activity, created = SimulatedActivity.objects.get_or_create(user=user)
            
            # Update all metrics
            activity.update_metrics()
            
            # Check if threshold is met
            if not activity.meets_analysis_threshold():
                logger.info(f"User {user.username} hasn't met analysis threshold yet")
                return None
            
            # Check if we should run a new prediction
            if self._should_run_new_prediction(user, activity):
                return self._run_prediction(user, activity)
            
            return None
            
        except SimulatedUser.DoesNotExist:
            logger.error(f"SimulatedUser with id {user_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error in check_and_predict for user {user_id}: {str(e)}")
            return None
    
    def _should_run_new_prediction(self, user, activity):
        """
        Determine if we should run a new prediction based on activity changes.
        """
        latest_prediction = user.predictions.filter(is_latest=True).first()
        
        # Always predict if no previous prediction
        if not latest_prediction:
            return True
        
        # Get the previous activity snapshot
        previous_features = latest_prediction.features_snapshot
        current_features = self._extract_features_from_activity(activity)
        
        # Check for significant changes that warrant new prediction
        significant_changes = [
            # New posts (every 3 posts)
            current_features['post_count'] >= previous_features.get('post_count', 0) + 3,
            
            # Many new likes (every 10 likes)
            current_features['follower_count'] >= previous_features.get('follower_count', 0) + 10,
            
            # New comments (every 5 comments)
            activity.total_comments_given >= previous_features.get('avg_comments_per_post', 0) * previous_features.get('post_count', 1) + 5,
            
            # Profile changes
            current_features['has_profile_pic'] != previous_features.get('has_profile_pic', False),
            current_features['has_external_url'] != previous_features.get('has_external_url', False),
            current_features['bio_length'] != previous_features.get('bio_length', 0),
            
            # Time-based: re-analyze every 5 minutes of activity
            activity.session_duration >= 300 and (timezone.now() - latest_prediction.predicted_at).total_seconds() >= 300
        ]
        
        return any(significant_changes)
    
    def _run_prediction(self, user, activity):
        """
        Run the actual prediction using the ML model.
        """
        try:
            logger.info(f"Running prediction for user {user.username}")
            
            # Extract features for the model
            features = self._extract_features_from_activity(activity)
            
            # Run prediction using existing model
            if not self.predictor.is_model_loaded():
                logger.error("ML model not loaded")
                return None

            result = self.predictor.predict(features)
            
            if not result:
                logger.error("Prediction failed")
                return None
            
            # Create prediction record
            prediction = SimulatedPrediction.objects.create(
                user=user,
                prediction=result['prediction'],
                confidence_score=result['confidence'],  # Already in decimal format
                features_snapshot=features,
                shap_values=result.get('shap_values', {}),
                top_features=result.get('top_features', []),
                is_latest=True
            )
            
            logger.info(f"Prediction saved for {user.username}: {prediction.prediction} ({prediction.confidence_score:.1%})")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error running prediction for {user.username}: {str(e)}")
            return None
    
    def _extract_features_from_activity(self, activity):
        """
        Convert SimulatedActivity to the exact format needed by XGBoost model.
        Returns dict with exact feature names expected by the model.
        """
        # Calculate follower/following ratio
        if activity.calculated_following_count > 0:
            follower_following_ratio = activity.calculated_follower_count / activity.calculated_following_count
        else:
            follower_following_ratio = float('inf') if activity.calculated_follower_count > 0 else 0
        
        # Calculate average likes and comments per post
        if activity.total_posts > 0:
            # Get actual likes and comments from posts
            total_likes = sum(post.likes_count for post in activity.user.posts.all())
            total_comments = sum(post.comments.count() for post in activity.user.posts.all())
            
            avg_likes_per_post = total_likes / activity.total_posts
            avg_comments_per_post = total_comments / activity.total_posts
        else:
            avg_likes_per_post = 0.0
            avg_comments_per_post = 0.0
        
        features = {
            'follower_count': activity.calculated_follower_count,
            'following_count': activity.calculated_following_count,
            'post_count': activity.total_posts,
            'follower_following_ratio': follower_following_ratio,
            'bio_length': activity.bio_length,
            'has_profile_pic': 1 if activity.has_profile_pic else 0,
            'has_external_url': 1 if activity.has_external_url else 0,
            'avg_likes_per_post': avg_likes_per_post,
            'avg_comments_per_post': avg_comments_per_post,
            'engagement_rate': activity.engagement_rate,
            'is_private': 0,  # Simulation accounts are never private
        }
        
        logger.debug(f"Extracted features for {activity.user.username}: {features}")
        
        return features
    
    def force_reanalyze(self, user_id):
        """
        Force immediate re-analysis of a user regardless of thresholds.
        Used by the dashboard "Re-analyze Now" button.
        """
        try:
            user = SimulatedUser.objects.get(id=user_id)
            activity, created = SimulatedActivity.objects.get_or_create(user=user)
            
            # Update metrics
            activity.update_metrics()
            
            # Run prediction regardless of threshold
            return self._run_prediction(user, activity)
            
        except Exception as e:
            logger.error(f"Error in force_reanalyze for user {user_id}: {str(e)}")
            return None
    
    def get_dashboard_data(self):
        """
        Get all data needed for the analytics dashboard.
        Returns comprehensive statistics and user data.
        """
        try:
            # Get all non-bot users
            users = SimulatedUser.objects.filter(is_bot=False).select_related('activity')
            
            # Get latest predictions
            latest_predictions = SimulatedPrediction.objects.filter(is_latest=True).select_related('user')
            
            # Calculate statistics
            total_users = users.count()
            real_count = latest_predictions.filter(prediction='Real').count()
            fake_count = latest_predictions.filter(prediction='Fake').count()
            pending_count = total_users - (real_count + fake_count)
            
            # Calculate average confidence
            predictions_with_confidence = latest_predictions.exclude(confidence_score__isnull=True)
            if predictions_with_confidence.exists():
                avg_confidence = sum(p.confidence_score for p in predictions_with_confidence) / predictions_with_confidence.count()
            else:
                avg_confidence = 0.0
            
            # Get total activity stats
            total_posts = sum(user.posts.count() for user in users)
            total_likes = sum(user.likes_given.count() for user in users)
            total_comments = sum(user.comments_given.count() for user in users)
            
            # Prepare user data for dashboard
            user_data = []
            for user in users:
                # Get latest prediction
                latest_pred = latest_predictions.filter(user=user).first()
                
                # Get activity summary
                activity_summary = self._get_activity_summary(user)
                
                user_data.append({
                    'id': user.id,
                    'username': user.username,
                    'profile_pic': user.profile_picture.url if user.profile_picture else None,
                    'prediction': latest_pred.prediction if latest_pred else 'Pending',
                    'confidence': latest_pred.confidence_percentage if latest_pred else 0,
                    'confidence_score': latest_pred.confidence_score if latest_pred else 0,
                    'activity_summary': activity_summary,
                    'last_active': user.last_activity,
                    'created_at': user.created_at,
                    'session_duration': user.session_duration_minutes,
                })
            
            return {
                'stats': {
                    'total_users': total_users,
                    'total_real': real_count,
                    'total_fake': fake_count,
                    'pending': pending_count,
                    'avg_confidence': avg_confidence * 100,  # Convert to percentage
                    'total_posts': total_posts,
                    'total_interactions': total_likes + total_comments,
                },
                'users': user_data,
                'chart_data': {
                    'real_fake_distribution': {
                        'real': real_count,
                        'fake': fake_count,
                        'pending': pending_count,
                    }
                },
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return {
                'stats': {'total_users': 0, 'total_real': 0, 'total_fake': 0, 'pending': 0, 'avg_confidence': 0, 'total_posts': 0, 'total_interactions': 0},
                'users': [],
                'chart_data': {'real_fake_distribution': {'real': 0, 'fake': 0, 'pending': 0}},
                'last_updated': timezone.now().isoformat()
            }
    
    def _get_activity_summary(self, user):
        """
        Get activity summary string for a user.
        """
        posts_count = user.posts.count()
        likes_count = user.likes_given.count()
        comments_count = user.comments_given.count()
        
        return f"{posts_count} posts • {likes_count} likes • {comments_count} comments"
    
    def get_user_detail(self, user_id):
        """
        Get detailed information about a specific user for the user detail page.
        """
        try:
            user = SimulatedUser.objects.get(id=user_id)
            activity, created = SimulatedActivity.objects.get_or_create(user=user)
            
            # Get prediction history
            predictions = user.predictions.all().order_by('-predicted_at')
            latest_prediction = predictions.first()
            
            # Get recent activity timeline
            recent_actions = self._get_recent_activity_timeline(user)
            
            # Get extracted features
            features = self._extract_features_from_activity(activity) if latest_prediction else {}
            
            return {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'bio': user.bio,
                    'profile_picture': user.profile_picture.url if user.profile_picture else None,
                    'external_url': user.external_url,
                    'created_at': user.created_at,
                    'session_duration': user.session_duration_minutes,
                    'last_activity': user.last_activity,
                },
                'latest_prediction': {
                    'prediction': latest_prediction.prediction if latest_prediction else 'Pending',
                    'confidence': latest_prediction.confidence_percentage if latest_prediction else 0,
                    'predicted_at': latest_prediction.predicted_at if latest_prediction else None,
                    'risk_level': latest_prediction.risk_level if latest_prediction else 'Unknown',
                    'top_features': latest_prediction.top_features if latest_prediction else [],
                } if latest_prediction else None,
                'prediction_history': [
                    {
                        'prediction': pred.prediction,
                        'confidence': pred.confidence_percentage,
                        'predicted_at': pred.predicted_at,
                    }
                    for pred in predictions
                ],
                'activity_metrics': {
                    'total_posts': activity.total_posts,
                    'total_likes_given': activity.total_likes_given,
                    'total_comments_given': activity.total_comments_given,
                    'bio_length': activity.bio_length,
                    'has_profile_pic': activity.has_profile_pic,
                    'has_external_url': activity.has_external_url,
                    'calculated_follower_count': activity.calculated_follower_count,
                    'calculated_following_count': activity.calculated_following_count,
                    'engagement_rate': activity.engagement_rate,
                    'username_entropy': activity.username_entropy,
                },
                'extracted_features': features,
                'recent_activity': recent_actions,
                'meets_threshold': activity.meets_analysis_threshold(),
            }
            
        except Exception as e:
            logger.error(f"Error getting user detail for {user_id}: {str(e)}")
            return None
    
    def _get_recent_activity_timeline(self, user, limit=20):
        """
        Get recent activity timeline for a user.
        """
        actions = []
        
        # Get recent posts
        for post in user.posts.all()[:limit//3]:
            actions.append({
                'type': 'post',
                'description': f'Posted a photo',
                'timestamp': post.created_at,
                'details': post.caption[:50] + '...' if len(post.caption) > 50 else post.caption
            })
        
        # Get recent likes
        for like in user.likes_given.all()[:limit//3]:
            actions.append({
                'type': 'like',
                'description': f'Liked {like.post.user.username}\'s post',
                'timestamp': like.created_at,
                'details': ''
            })
        
        # Get recent comments
        for comment in user.comments_given.all()[:limit//3]:
            actions.append({
                'type': 'comment',
                'description': f'Commented on {comment.post.user.username}\'s post',
                'timestamp': comment.created_at,
                'details': comment.text[:50] + '...' if len(comment.text) > 50 else comment.text
            })
        
        # Sort by timestamp
        actions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return actions[:limit]


# Global analyzer instance
analyzer = SimulationAnalyzer()


def trigger_analysis(user_id):
    """
    Convenience function to trigger analysis after user actions.
    Call this after posts, likes, comments, profile updates.
    """
    return analyzer.check_and_predict(user_id)
