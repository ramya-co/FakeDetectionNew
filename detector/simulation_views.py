"""
Views for Instagram simulation functionality.
"""
import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.core.paginator import Paginator

from detector.models import SimulatedUser, SimulatedPost, SimulatedLike, SimulatedComment, SimulatedActivity, SimulatedPrediction
from .simulation_analyzer import trigger_analysis, analyzer

logger = logging.getLogger(__name__)


def simulation_intro(request):
    """
    Simulation intro page with two buttons:
    1. Start Simulation (Instagram Clone)
    2. View Dashboard (Analytics)
    """
    return render(request, 'simulation/intro.html')


def create_account(request):
    """
    Create account form for entering the Instagram simulation.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        bio = request.POST.get('bio', '').strip()
        external_url = request.POST.get('external_url', '').strip()
        profile_picture = request.FILES.get('profile_picture')
        
        # Validate username
        if not username:
            return render(request, 'simulation/create_account.html', {
                'error': 'Username is required'
            })
        
        if SimulatedUser.objects.filter(username=username).exists():
            return render(request, 'simulation/create_account.html', {
                'error': 'Username already exists. Please choose another.'
            })
        
        try:
            # Create user
            user = SimulatedUser.objects.create(
                username=username,
                bio=bio,
                external_url=external_url,
                profile_picture=profile_picture
            )
            
            # Create activity record
            SimulatedActivity.objects.create(user=user)
            
            # Store user ID in session
            request.session['simulated_user_id'] = user.id
            
            # Redirect to Instagram clone
            return redirect('simulation:instagram_clone')
            
        except Exception as e:
            logger.error(f"Error creating simulated user: {str(e)}")
            return render(request, 'simulation/create_account.html', {
                'error': 'An error occurred. Please try again.'
            })
    
    return render(request, 'simulation/create_account.html')


def instagram_clone(request):
    """
    Main Instagram clone interface.
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return redirect('simulation:create_account')
    
    try:
        user = SimulatedUser.objects.get(id=user_id)
        
        # Update last activity
        user.last_activity = timezone.now()
        user.save(update_fields=['last_activity'])
        
        # Get feed posts (user's posts + some bot posts for realistic experience)
        user_posts = user.posts.all()[:10]
        bot_posts = SimulatedPost.objects.filter(user__is_bot=True)[:20]
        
        # Combine and sort by creation date
        all_posts = list(user_posts) + list(bot_posts)
        all_posts.sort(key=lambda x: x.created_at, reverse=True)
        
        context = {
            'user': user,
            'posts': all_posts[:30],  # Limit to 30 posts
            'user_posts_count': user.posts.count(),
            'user_likes_count': user.likes_given.count(),
            'user_comments_count': user.comments_given.count(),
        }
        
        return render(request, 'simulation/instagram_clone.html', context)
        
    except SimulatedUser.DoesNotExist:
        # Clear invalid session
        del request.session['simulated_user_id']
        return redirect('simulation:create_account')


@csrf_exempt
@require_http_methods(["POST"])
def create_post(request):
    """
    API endpoint to create a new post.
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        user = SimulatedUser.objects.get(id=user_id)
        
        # Get form data
        image = request.FILES.get('image')
        caption = request.POST.get('caption', '').strip()
        location = request.POST.get('location', '').strip()
        
        if not image:
            return render(request, 'simulation/instagram_clone.html', {
                'error': 'Please select an image to post',
                'user': user,
                'posts': []
            })
        
        # Validate image file
        if not image.content_type.startswith('image/'):
            return render(request, 'simulation/instagram_clone.html', {
                'error': 'Please upload a valid image file',
                'user': user,
                'posts': []
            })
        
        # Create post
        post = SimulatedPost.objects.create(
            user=user,
            image=image,
            caption=caption,
            location=location
        )
        
        # Trigger analysis after post creation
        trigger_analysis(user.id)
        
        return redirect('simulation:instagram_clone')
        
    except SimulatedUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        return JsonResponse({'error': 'Failed to create post'}, status=500)


@csrf_exempt  
@require_http_methods(["POST"])
def toggle_like(request, post_id):
    """
    AJAX endpoint to toggle like on a post.
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        user = SimulatedUser.objects.get(id=user_id)
        post = SimulatedPost.objects.get(id=post_id)
        
        # Check if already liked
        like, created = SimulatedLike.objects.get_or_create(
            user=user,
            post=post,
            defaults={'created_at': timezone.now()}
        )
        
        if not created:
            # Unlike the post
            like.delete()
            liked = False
        else:
            liked = True
            # Trigger analysis after like action
            trigger_analysis(user.id)
        
        # Get updated likes count
        likes_count = post.likes.count()
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': likes_count
        })
        
    except (SimulatedUser.DoesNotExist, SimulatedPost.DoesNotExist):
        return JsonResponse({'error': 'User or post not found'}, status=404)
    except Exception as e:
        logger.error(f"Error toggling like: {str(e)}")
        return JsonResponse({'error': 'Failed to toggle like'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])  
def add_comment(request, post_id):
    """
    AJAX endpoint to add a comment to a post.
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        user = SimulatedUser.objects.get(id=user_id)
        post = SimulatedPost.objects.get(id=post_id)
        
        # Get comment text from request body
        data = json.loads(request.body)
        comment_text = data.get('text', '').strip()
        
        if not comment_text:
            return JsonResponse({'error': 'Comment text is required'}, status=400)
        
        # Create comment
        comment = SimulatedComment.objects.create(
            user=user,
            post=post,
            text=comment_text
        )
        
        # Trigger analysis after comment action
        trigger_analysis(user.id)
        
        return JsonResponse({
            'success': True,
            'username': user.username,
            'comment_id': comment.id
        })
        
    except (SimulatedUser.DoesNotExist, SimulatedPost.DoesNotExist):
        return JsonResponse({'error': 'User or post not found'}, status=404)
    except Exception as e:
        logger.error(f"Error adding comment: {str(e)}")
        return JsonResponse({'error': 'Failed to add comment'}, status=500)
        trigger_analysis(user_id)
        
        return JsonResponse({
            'success': True,
            'post_id': post.id,
            'message': 'Post created successfully!'
        })
        
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        return JsonResponse({'error': 'Failed to create post'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_like(request):
    """
    API endpoint to like/unlike a post.
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        data = json.loads(request.body)
        post_id = data.get('post_id')
        
        if not post_id:
            return JsonResponse({'error': 'Post ID required'}, status=400)
        
        user = SimulatedUser.objects.get(id=user_id)
        post = SimulatedPost.objects.get(id=post_id)
        
        # Check if already liked
        existing_like = SimulatedLike.objects.filter(user=user, post=post).first()
        
        if existing_like:
            # Unlike
            existing_like.delete()
            post.update_likes_count()
            liked = False
        else:
            # Like
            SimulatedLike.objects.create(user=user, post=post)
            post.update_likes_count()
            liked = True
            
            # Trigger analysis after like
            trigger_analysis(user_id)
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': post.likes_count
        })
        
    except Exception as e:
        logger.error(f"Error toggling like: {str(e)}")
        return JsonResponse({'error': 'Failed to toggle like'}, status=500)


@require_http_methods(["GET"])
def get_feed(request):
    """
    API endpoint to get feed posts (for infinite scroll or refresh).
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        page = int(request.GET.get('page', 1))
        per_page = 10
        
        user = SimulatedUser.objects.get(id=user_id)
        
        # Get all posts (user's + bot posts)
        all_posts = SimulatedPost.objects.all().order_by('-created_at')
        
        paginator = Paginator(all_posts, per_page)
        posts_page = paginator.get_page(page)
        
        posts_data = []
        for post in posts_page:
            # Check if current user liked this post
            user_liked = SimulatedLike.objects.filter(user=user, post=post).exists()
            
            # Get recent comments
            comments = post.comments.all()[:3]
            
            posts_data.append({
                'id': post.id,
                'username': post.user.username,
                'profile_pic': post.user.profile_picture.url if post.user.profile_picture else None,
                'image': post.image.url,
                'caption': post.caption,
                'location': post.location,
                'likes_count': post.likes_count,
                'comments_count': post.comments.count(),
                'created_at': post.created_at.strftime('%Y-%m-%d %H:%M'),
                'user_liked': user_liked,
                'recent_comments': [
                    {
                        'id': comment.id,
                        'username': comment.user.username,
                        'text': comment.text,
                        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
                    }
                    for comment in comments
                ]
            })
        
        return JsonResponse({
            'success': True,
            'posts': posts_data,
            'has_next': posts_page.has_next(),
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Error getting feed: {str(e)}")
        return JsonResponse({'error': 'Failed to get feed'}, status=500)


def user_profile(request):
    """
    Show current user's profile page.
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return redirect('simulation:create_account')
    
    try:
        user = SimulatedUser.objects.get(id=user_id)
        posts = user.posts.all().order_by('-created_at')
        
        # Get latest prediction if available
        latest_prediction = user.predictions.filter(is_latest=True).first()
        
        context = {
            'user': user,
            'posts': posts,
            'posts_count': posts.count(),
            'likes_given_count': user.likes_given.count(),
            'comments_given_count': user.comments_given.count(),
            'latest_prediction': latest_prediction,
        }
        
        return render(request, 'simulation/user_profile.html', context)
        
    except SimulatedUser.DoesNotExist:
        del request.session['simulated_user_id']
        return redirect('simulation:create_account')


@csrf_exempt
@require_http_methods(["POST"])
def update_profile(request):
    """
    API endpoint to update user profile.
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    try:
        user = SimulatedUser.objects.get(id=user_id)
        
        # Get updated data
        bio = request.POST.get('bio', '').strip()
        external_url = request.POST.get('external_url', '').strip()
        profile_picture = request.FILES.get('profile_picture')
        
        # Update fields
        user.bio = bio
        user.external_url = external_url
        
        if profile_picture:
            user.profile_picture = profile_picture
        
        user.save()
        
        # Trigger analysis after profile update
        trigger_analysis(user_id)
        
        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully!'
        })
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return JsonResponse({'error': 'Failed to update profile'}, status=500)


def end_simulation(request):
    """
    End simulation and show user's results.
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return redirect('simulation:create_account')
    
    try:
        user = SimulatedUser.objects.get(id=user_id)
        
        # Mark session as ended
        user.session_end = timezone.now()
        user.is_active = False
        user.save()
        
        # Get user's detailed results
        user_detail = analyzer.get_user_detail(user_id)
        
        # Clear session
        del request.session['simulated_user_id']
        
        return render(request, 'simulation/results.html', {
            'user_detail': user_detail
        })
        
    except SimulatedUser.DoesNotExist:
        return redirect('simulation:create_account')


def user_profile(request):
    """
    User profile page showing user's posts and stats.
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return redirect('simulation:create_account')
    
    try:
        user = SimulatedUser.objects.get(id=user_id)
        user_posts = user.posts.all().order_by('-created_at')
        
        # Get user stats
        context = {
            'user': user,
            'posts': user_posts,
            'posts_count': user_posts.count(),
            'likes_count': user.likes_given.count(),
            'comments_count': user.comments_given.count(),
        }
        
        return render(request, 'simulation/user_profile.html', context)
        
    except SimulatedUser.DoesNotExist:
        del request.session['simulated_user_id']
        return redirect('simulation:create_account')


def end_simulation(request):
    """
    End the simulation and show results.
    """
    user_id = request.session.get('simulated_user_id')
    
    if not user_id:
        return redirect('simulation:intro')
    
    try:
        user = SimulatedUser.objects.get(id=user_id)
        
        # Get final analysis
        user_detail = analyzer.get_user_detail(user.id)
        
        # Clear session
        if 'simulated_user_id' in request.session:
            del request.session['simulated_user_id']
        
        return render(request, 'simulation/results.html', {
            'user_detail': user_detail,
            'user': user
        })
        
    except SimulatedUser.DoesNotExist:
        if 'simulated_user_id' in request.session:
            del request.session['simulated_user_id']
        return redirect('simulation:intro')
