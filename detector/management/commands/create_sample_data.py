"""
Management command to create sample bot users and posts for Instagram simulation.
"""
import random
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import requests
from detector.models import SimulatedUser, SimulatedPost


class Command(BaseCommand):
    help = 'Create sample bot users and posts for Instagram simulation'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample bot users and posts...')
        
        # Sample bot usernames and bios
        bot_data = [
            {'username': 'photography_pro', 'bio': '📸 Professional photographer | Travel enthusiast | DM for bookings'},
            {'username': 'travel_blogger', 'bio': '✈️ Exploring the world one city at a time | Food lover | Adventure seeker'},
            {'username': 'food_lover', 'bio': '🍕 Foodie | Restaurant reviews | Cooking tips | Follow for daily recipes'},
            {'username': 'fitness_guru', 'bio': '💪 Personal trainer | Fitness coach | Transform your life | Link in bio'},
            {'username': 'fashion_style', 'bio': '👗 Fashion enthusiast | Style tips | OOTD | Fashion blogger'},
            {'username': 'tech_insider', 'bio': '🚀 Tech news | Gadget reviews | Latest updates | Innovation enthusiast'},
            {'username': 'art_creator', 'bio': '🎨 Digital artist | Creative content | Art tutorials | Commission open'},
            {'username': 'music_beats', 'bio': '🎵 Music producer | Beat maker | New tracks weekly | Collab welcome'},
        ]
        
        # Sample captions
        captions = [
            "Beautiful sunset today! 🌅 #sunset #photography #nature",
            "Amazing food at this new restaurant! 🍽️ #foodie #restaurant #delicious",
            "Workout complete! 💪 #fitness #gym #motivation #health",
            "New art piece finished! 🎨 #art #creativity #digitalart #artist",
            "Travel memories from last week 📸 #travel #adventure #memories",
            "Latest tech gadget review is live! 📱 #tech #gadgets #review",
            "Fashion inspiration for today 👗 #fashion #style #ootd #trendy",
            "New music track dropping soon! 🎵 #music #producer #newrelease",
            "Coffee and creativity ☕ #morning #coffee #inspiration #work",
            "Weekend vibes are here! 🎉 #weekend #fun #relax #goodvibes"
        ]
        
        created_users = 0
        created_posts = 0
        
        for bot_info in bot_data:
            # Check if bot user already exists
            if SimulatedUser.objects.filter(username=bot_info['username']).exists():
                user = SimulatedUser.objects.get(username=bot_info['username'])
                self.stdout.write(f"Bot user {bot_info['username']} already exists")
            else:
                # Create bot user
                user = SimulatedUser.objects.create(
                    username=bot_info['username'],
                    bio=bot_info['bio'],
                    is_bot=True,
                    verified=random.choice([True, False]),
                    followers_count=random.randint(1000, 50000),
                    following_count=random.randint(200, 2000),
                    posts_count=random.randint(50, 500)
                )
                created_users += 1
                self.stdout.write(f"Created bot user: {bot_info['username']}")
            
            # Create 3-5 posts for each bot
            existing_posts = user.posts.count()
            posts_to_create = max(0, 5 - existing_posts)
            
            for i in range(posts_to_create):
                # Use a sample image from picsum.photos
                image_url = f"https://picsum.photos/800/800?random={user.id}{i}"
                
                try:
                    # Download the image
                    response = requests.get(image_url, timeout=10)
                    if response.status_code == 200:
                        image_content = ContentFile(response.content)
                        image_name = f"bot_post_{user.username}_{i}.jpg"
                        
                        # Create post
                        post = SimulatedPost.objects.create(
                            user=user,
                            caption=random.choice(captions),
                            likes_count=random.randint(10, 500),
                            comments_count=random.randint(0, 50)
                        )
                        
                        # Save the image
                        post.image.save(image_name, image_content, save=True)
                        created_posts += 1
                        
                        self.stdout.write(f"Created post for {user.username}")
                        
                except Exception as e:
                    self.stdout.write(f"Error creating post for {user.username}: {str(e)}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_users} bot users and {created_posts} posts'
            )
        )
