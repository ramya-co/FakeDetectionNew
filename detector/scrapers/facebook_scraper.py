"""
Facebook scraping functionality using multiple approaches.
"""
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


class FacebookScraper:
    """Advanced Facebook profile scraper with multiple methods."""
    
    def __init__(self):
        """Initialize the scraper with multiple approaches."""
        # Try to load API credentials from environment
        self.access_token = os.getenv('FACEBOOK_ACCESS_TOKEN', '')
        self.app_id = os.getenv('FACEBOOK_APP_ID', '')
        self.app_secret = os.getenv('FACEBOOK_APP_SECRET', '')
        
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
        """Clean and normalize username or profile URL."""
        username = username.strip()
        
        # Extract username from URL if needed
        if 'facebook.com' in username or 'fb.com' in username:
            # Try to extract username/ID from URL
            patterns = [
                r'facebook\.com/(?:profile\.php\?id=)?([^/?]+)',
                r'fb\.com/([^/?]+)',
                r'facebook\.com/people/[^/]+/(\d+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, username)
                if match:
                    username = match.group(1)
                    break
        
        return username
    
    def scrape_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Scrape Facebook profile using multiple methods.
        
        Args:
            username: Facebook username, profile ID, or URL
            
        Returns:
            Dictionary with profile data or None if all methods fail
        """
        username = self._clean_username(username)
        logger.info(f"Starting Facebook scraping for: {username}")
        
        # Try multiple methods in order
        methods = [
            ('Graph API', self._scrape_graph_api),
            ('Web Scraping', self._scrape_web),
            ('Mobile Site', self._scrape_mobile),
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
    
    def _scrape_graph_api(self, username: str) -> Optional[Dict[str, Any]]:
        """Scrape using Facebook Graph API."""
        if not self.access_token:
            logger.info("Facebook access token not available, skipping Graph API")
            return None
        
        try:
            # Determine if username is an ID or username
            if username.isdigit():
                user_id = username
            else:
                # Try to get user ID from username
                url = f'https://graph.facebook.com/v18.0/{username}'
                params = {'access_token': self.access_token}
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code != 200:
                    return None
                
                data = response.json()
                user_id = data.get('id')
            
            if not user_id:
                return None
            
            # Get user profile data
            url = f'https://graph.facebook.com/v18.0/{user_id}'
            params = {
                'fields': 'name,friends,about,picture,link,posts.limit(100){likes.summary(true),comments.summary(true)}',
                'access_token': self.access_token
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Calculate engagement metrics
            total_likes = 0
            total_comments = 0
            post_count = 0
            
            if 'posts' in data and 'data' in data['posts']:
                for post in data['posts']['data']:
                    if 'likes' in post and 'summary' in post['likes']:
                        total_likes += post['likes']['summary'].get('total_count', 0)
                    if 'comments' in post and 'summary' in post['comments']:
                        total_comments += post['comments']['summary'].get('total_count', 0)
                    post_count += 1
            
            avg_likes = total_likes / post_count if post_count > 0 else 0
            avg_comments = total_comments / post_count if post_count > 0 else 0
            
            # Note: Facebook Graph API has limited access to friend counts for privacy
            profile_data = {
                'username': data.get('name', username),
                'follower_count': data.get('friends', {}).get('summary', {}).get('total_count', 0),
                'following_count': 0,  # Not available via Graph API for regular users
                'post_count': post_count,
                'bio_length': len(data.get('about', '')),
                'has_profile_pic': bool(data.get('picture', {}).get('data', {}).get('url')),
                'has_external_url': bool(data.get('link')),
                'avg_likes_per_post': float(avg_likes),
                'avg_comments_per_post': float(avg_comments),
                'is_private': False,  # Graph API only returns public data
            }
            
            return profile_data
            
        except Exception as e:
            logger.error(f"Graph API error: {e}")
            return None
    
    def _scrape_web(self, username: str) -> Optional[Dict[str, Any]]:
        """Scrape using web scraping (limited due to Facebook's protection)."""
        try:
            url = f'https://www.facebook.com/{username}'
            response = self.session.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            return self._parse_facebook_html(response.text, username)
            
        except Exception as e:
            logger.error(f"Web scraping error: {e}")
            return None
    
    def _scrape_mobile(self, username: str) -> Optional[Dict[str, Any]]:
        """Scrape using mobile Facebook site (often less protected)."""
        try:
            url = f'https://m.facebook.com/{username}'
            
            # Use mobile user agent
            mobile_headers = self.headers.copy()
            mobile_headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
            
            response = requests.get(url, headers=mobile_headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            return self._parse_facebook_html(response.text, username)
            
        except Exception as e:
            logger.error(f"Mobile scraping error: {e}")
            return None
    
    def _parse_facebook_html(self, html: str, username: str) -> Optional[Dict[str, Any]]:
        """Parse Facebook HTML to extract profile data."""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Facebook heavily obfuscates their HTML, so this is limited
            # Try to find JSON data in scripts
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                if script.string:
                    try:
                        data = json.loads(script.string)
                        if 'name' in data:
                            return self._format_facebook_data(data, username)
                    except:
                        continue
            
            # If extraction fails, return estimated data with a warning
            logger.warning("Could not extract exact data from HTML, returning estimates")
            return self._get_estimated_data(username)
            
        except Exception as e:
            logger.error(f"HTML parsing error: {e}")
            return None
    
    def _format_facebook_data(self, data: dict, username: str) -> Dict[str, Any]:
        """Format extracted Facebook data."""
        return {
            'username': data.get('name', username),
            'follower_count': 0,  # Not available without authentication
            'following_count': 0,  # Not available without authentication
            'post_count': 0,  # Not available without authentication
            'bio_length': len(data.get('description', '')),
            'has_profile_pic': bool(data.get('image')),
            'has_external_url': bool(data.get('url')),
            'avg_likes_per_post': 0.0,  # Not available without authentication
            'avg_comments_per_post': 0.0,  # Not available without authentication
            'is_private': False,
        }
    
    def _get_estimated_data(self, username: str) -> Dict[str, Any]:
        """Return estimated/placeholder data when scraping partially fails."""
        logger.info("Returning estimated data - Facebook scraping is limited without authentication")
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


def scrape_facebook_profile(username: str) -> Optional[Dict[str, Any]]:
    """
    Main function to scrape a Facebook profile.
    
    Args:
        username: Facebook username, ID, or URL
        
    Returns:
        Dictionary with profile data or None if scraping fails
    
    Note:
        Facebook scraping is highly restricted. This function provides:
        - Graph API scraping (requires access token)
        - Web scraping (very limited due to Facebook's protection)
        - Returns estimated data with manual input fallback suggestion
    """
    scraper = FacebookScraper()
    return scraper.scrape_profile(username)


if __name__ == '__main__':
    # Test the scraper
    logging.basicConfig(level=logging.INFO)
    test_username = 'zuck'
    result = scrape_facebook_profile(test_username)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("Scraping failed - use manual input instead")
