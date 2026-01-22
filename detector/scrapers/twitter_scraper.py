"""
Twitter/X scraping functionality using multiple approaches.
"""
import tweepy
import requests
import json
import time
import logging
import random
from typing import Optional, Dict, Any
import re
from bs4 import BeautifulSoup
import os

logger = logging.getLogger('detector')


class TwitterScraper:
    """Advanced Twitter/X profile scraper with multiple methods."""
    
    def __init__(self):
        """Initialize the scraper with multiple approaches."""
        # Try to load API credentials from environment
        self.api_key = os.getenv('TWITTER_API_KEY', '')
        self.api_secret = os.getenv('TWITTER_API_SECRET', '')
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '')
        
        self.client = None
        if self.bearer_token:
            try:
                self.client = tweepy.Client(bearer_token=self.bearer_token)
            except Exception as e:
                logger.warning(f"Could not initialize Twitter API client: {e}")
        
        # Web scraping headers
        self.headers = self._get_random_headers()
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _get_random_headers(self):
        """Get randomized headers to avoid detection."""
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def _clean_username(self, username: str) -> str:
        """Clean and normalize username."""
        username = username.strip()
        if username.startswith('@'):
            username = username[1:]
        
        # Extract username from URL if needed
        if 'twitter.com' in username or 'x.com' in username:
            match = re.search(r'(?:twitter\.com|x\.com)/([^/?]+)', username)
            if match:
                username = match.group(1)
        
        return username
    
    def scrape_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Scrape Twitter profile using multiple methods.
        
        Args:
            username: Twitter username (without @)
            
        Returns:
            Dictionary with profile data or None if all methods fail
        """
        username = self._clean_username(username)
        logger.info(f"Starting Twitter scraping for: {username}")
        
        # Try multiple methods in order
        methods = [
            ('Twitter API', self._scrape_api),
            ('Web Scraping', self._scrape_web),
            ('Nitter Fallback', self._scrape_nitter),
        ]
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name} for {username}")
                profile_data = method_func(username)
                
                if profile_data and self._validate_profile_data(profile_data):
                    logger.info(f"✅ Successfully scraped {username} using {method_name}")
                    return profile_data
                else:
                    logger.warning(f"❌ {method_name} failed or returned invalid data")
                    
            except Exception as e:
                logger.warning(f"❌ {method_name} error for {username}: {str(e)}")
                continue
            
            time.sleep(random.uniform(1, 2))
        
        logger.error(f"All scraping methods failed for {username}")
        return None
    
    def _scrape_api(self, username: str) -> Optional[Dict[str, Any]]:
        """Scrape using Twitter API v2."""
        if not self.client:
            logger.info("Twitter API client not initialized, skipping")
            return None
        
        try:
            # Get user info
            user = self.client.get_user(
                username=username,
                user_fields=['public_metrics', 'description', 'profile_image_url', 'url', 'protected']
            )
            
            if not user.data:
                return None
            
            user_data = user.data
            metrics = user_data.public_metrics
            
            # Get recent tweets for engagement calculation
            tweets = self.client.get_users_tweets(
                id=user_data.id,
                max_results=100,
                tweet_fields=['public_metrics']
            )
            
            # Calculate average engagement
            total_likes = 0
            total_retweets = 0
            total_replies = 0
            tweet_count = 0
            
            if tweets.data:
                for tweet in tweets.data:
                    tweet_metrics = tweet.public_metrics
                    total_likes += tweet_metrics.get('like_count', 0)
                    total_retweets += tweet_metrics.get('retweet_count', 0)
                    total_replies += tweet_metrics.get('reply_count', 0)
                    tweet_count += 1
            
            avg_likes = total_likes / tweet_count if tweet_count > 0 else 0
            avg_comments = (total_replies + total_retweets) / tweet_count if tweet_count > 0 else 0
            
            profile_data = {
                'username': username,
                'follower_count': metrics.get('followers_count', 0),
                'following_count': metrics.get('following_count', 0),
                'post_count': metrics.get('tweet_count', 0),
                'bio_length': len(user_data.description) if user_data.description else 0,
                'has_profile_pic': bool(user_data.profile_image_url),
                'has_external_url': bool(user_data.url),
                'avg_likes_per_post': float(avg_likes),
                'avg_comments_per_post': float(avg_comments),
                'is_private': bool(user_data.protected),
            }
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Twitter API error: {e}")
            return None
    
    def _scrape_web(self, username: str) -> Optional[Dict[str, Any]]:
        """Scrape using web scraping (fallback method)."""
        try:
            # Try both twitter.com and x.com
            urls = [
                f'https://twitter.com/{username}',
                f'https://x.com/{username}'
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=10)
                    if response.status_code == 200:
                        return self._parse_twitter_html(response.text, username)
                except Exception as e:
                    logger.debug(f"Failed to fetch {url}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Web scraping error: {e}")
            return None
    
    def _parse_twitter_html(self, html: str, username: str) -> Optional[Dict[str, Any]]:
        """Parse Twitter HTML to extract profile data."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try to find JSON data in scripts
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'followers_count' in script.string:
                    # Extract JSON data
                    try:
                        json_match = re.search(r'\{[^{}]*"followers_count"[^{}]*\}', script.string)
                        if json_match:
                            data = json.loads(json_match.group())
                            return self._format_twitter_data(data, username)
                    except:
                        continue
            
            # If JSON extraction fails, return estimated data
            logger.warning("Could not extract exact data, returning estimates")
            return self._get_estimated_data(username)
            
        except Exception as e:
            logger.error(f"HTML parsing error: {e}")
            return None
    
    def _scrape_nitter(self, username: str) -> Optional[Dict[str, Any]]:
        """Scrape using Nitter instances (privacy-friendly Twitter frontend)."""
        nitter_instances = [
            'https://nitter.net',
            'https://nitter.poast.org',
            'https://nitter.privacydev.net',
        ]
        
        for instance in nitter_instances:
            try:
                url = f'{instance}/{username}'
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract stats from Nitter page
                    stats = soup.find_all('span', class_='profile-stat-num')
                    if len(stats) >= 3:
                        profile_data = {
                            'username': username,
                            'post_count': self._parse_count(stats[0].text),
                            'following_count': self._parse_count(stats[1].text),
                            'follower_count': self._parse_count(stats[2].text),
                            'bio_length': len(soup.find('p', class_='profile-bio').text) if soup.find('p', class_='profile-bio') else 0,
                            'has_profile_pic': bool(soup.find('img', class_='avatar')),
                            'has_external_url': bool(soup.find('a', class_='profile-website')),
                            'avg_likes_per_post': 0.0,  # Nitter doesn't provide this
                            'avg_comments_per_post': 0.0,  # Nitter doesn't provide this
                            'is_private': False,
                        }
                        return profile_data
                        
            except Exception as e:
                logger.debug(f"Nitter instance {instance} failed: {e}")
                continue
        
        return None
    
    def _parse_count(self, text: str) -> int:
        """Parse count with K/M suffixes."""
        text = text.strip().replace(',', '')
        if 'K' in text:
            return int(float(text.replace('K', '')) * 1000)
        elif 'M' in text:
            return int(float(text.replace('M', '')) * 1000000)
        else:
            try:
                return int(text)
            except:
                return 0
    
    def _format_twitter_data(self, data: dict, username: str) -> Dict[str, Any]:
        """Format extracted Twitter data."""
        return {
            'username': username,
            'follower_count': data.get('followers_count', 0),
            'following_count': data.get('friends_count', 0),
            'post_count': data.get('statuses_count', 0),
            'bio_length': len(data.get('description', '')),
            'has_profile_pic': bool(data.get('profile_image_url')),
            'has_external_url': bool(data.get('url')),
            'avg_likes_per_post': 0.0,  # Would need additional API calls
            'avg_comments_per_post': 0.0,  # Would need additional API calls
            'is_private': data.get('protected', False),
        }
    
    def _get_estimated_data(self, username: str) -> Dict[str, Any]:
        """Return estimated/placeholder data when scraping partially fails."""
        return {
            'username': username,
            'follower_count': 0,
            'following_count': 0,
            'post_count': 0,
            'bio_length': 0,
            'has_profile_pic': True,
            'has_external_url': False,
            'avg_likes_per_post': 0.0,
            'avg_comments_per_post': 0.0,
            'is_private': False,
        }
    
    def _validate_profile_data(self, data: Dict[str, Any]) -> bool:
        """Validate that profile data has required fields."""
        required_fields = [
            'username', 'follower_count', 'following_count', 'post_count',
            'bio_length', 'has_profile_pic', 'has_external_url',
            'avg_likes_per_post', 'avg_comments_per_post', 'is_private'
        ]
        return all(field in data for field in required_fields)


def scrape_twitter_profile(username: str) -> Optional[Dict[str, Any]]:
    """
    Main function to scrape a Twitter profile.
    
    Args:
        username: Twitter username or URL
        
    Returns:
        Dictionary with profile data or None if scraping fails
    """
    scraper = TwitterScraper()
    return scraper.scrape_profile(username)


if __name__ == '__main__':
    # Test the scraper
    logging.basicConfig(level=logging.INFO)
    test_username = 'elonmusk'
    result = scrape_twitter_profile(test_username)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Scraping failed")
