"""
Instagram scraping functionality using multiple approaches.
"""
import instaloader
import requests
import json
import time
import logging
import random
from typing import Optional, Dict, Any
import re
from bs4 import BeautifulSoup
import urllib.parse

logger = logging.getLogger('detector')


class InstagramScraper:
    """Advanced Instagram profile scraper with multiple methods."""
    
    def __init__(self):
        """Initialize the scraper with multiple approaches."""
        # Method 1: Instaloader
        self.loader = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            quiet=True
        )
        
        # Method 2: Web scraping headers
        self.headers = self._get_random_headers()
        
        # Method 3: Session for consistency
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
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
    def scrape_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Scrape Instagram profile using multiple methods for better success rate.
        
        Args:
            username: Instagram username (without @)
            
        Returns:
            Dictionary with profile data or None if all methods fail
        """
        username = self._clean_username(username)
        logger.info(f"Starting multi-method scraping for: {username}")
        
        # Try multiple methods in order of reliability
        methods = [
            ('Web Scraping (Direct)', self._scrape_web_direct),
            ('Web Scraping (Embedded)', self._scrape_web_embedded), 
            ('Instaloader', self._scrape_instaloader),
            ('Public API', self._scrape_public_api)
        ]
        
        for method_name, method_func in methods:
            try:
                logger.info(f"Trying {method_name} for {username}")
                profile_data = method_func(username)
                
                if profile_data and self._validate_profile_data(profile_data):
                    logger.info(f"✅ Successfully scraped {username} using {method_name}")
                    return profile_data
                else:
                    logger.warning(f"❌ {method_name} failed or returned invalid data for {username}")
                    
            except Exception as e:
                logger.warning(f"❌ {method_name} error for {username}: {str(e)}")
                continue
            
            # Add delay between methods
            time.sleep(random.uniform(1, 3))
        
        logger.error(f"❌ All scraping methods failed for {username}")
        return None
    
    def _clean_username(self, username: str) -> str:
        """Clean and validate username."""
        username = username.strip().lower()
        if username.startswith('@'):
            username = username[1:]
        return username
    
    def _validate_profile_data(self, data: Dict[str, Any]) -> bool:
        """Validate that profile data has minimum required fields."""
        required_fields = ['username', 'follower_count', 'following_count', 'post_count']
        return all(field in data and data[field] is not None for field in required_fields)
    
    def _scrape_web_direct(self, username: str) -> Optional[Dict[str, Any]]:
        """Method 1: Enhanced direct web scraping with multiple strategies."""
        try:
            url = f"https://www.instagram.com/{username}/"
            logger.info(f"Direct scraping: {url}")
            
            # Random delay
            time.sleep(random.uniform(1, 3))
            
            # Try mobile endpoint first (often has more accessible data)
            mobile_url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
            try:
                response = self.session.get(mobile_url, timeout=10)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        result = self._parse_api_data(data, username)
                        if result and result.get('follower_count', 0) > 0:
                            logger.info(f"Successfully extracted from mobile API: {username}")
                            return result
                    except json.JSONDecodeError:
                        pass
            except:
                pass
            
            # Regular page scraping
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 404:
                logger.error(f"Profile {username} not found (404)")
                return None
            elif response.status_code != 200:
                logger.error(f"HTTP {response.status_code} for {username}")
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Strategy 1: Extract JSON-LD data
            scripts = soup.find_all('script', type='application/ld+json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if '@type' in data and 'Person' in str(data.get('@type', '')):
                        result = self._parse_json_ld_data(data, username)
                        if result and result.get('follower_count', 0) > 0:
                            return result
                except:
                    continue
            
            # Strategy 2: Extract from window._sharedData and other JS variables
            for script in soup.find_all('script'):
                if not script.string:
                    continue
                    
                script_content = script.string
                
                # Pattern 1: window._sharedData
                if 'window._sharedData' in script_content:
                    try:
                        json_str = script_content.split('window._sharedData = ')[1].split(';</script>')[0]
                        data = json.loads(json_str)
                        result = self._parse_shared_data(data, username)
                        if result and result.get('follower_count', 0) > 0:
                            return result
                    except:
                        continue
                
                # Pattern 2: Look for any embedded JSON with user data
                if '"edge_followed_by"' in script_content or '"follower_count"' in script_content:
                    try:
                        # Extract follower/following/post counts from any JSON structure
                        followers = self._extract_count_from_script(script_content, [
                            r'"edge_followed_by":\s*{"count":\s*(\d+)}',
                            r'"follower_count":\s*(\d+)'
                        ])
                        
                        following = self._extract_count_from_script(script_content, [
                            r'"edge_follow":\s*{"count":\s*(\d+)}',
                            r'"following_count":\s*(\d+)'
                        ])
                        
                        posts = self._extract_count_from_script(script_content, [
                            r'"edge_owner_to_timeline_media":\s*{"count":\s*(\d+)}',
                            r'"media_count":\s*(\d+)'
                        ])
                        
                        if followers > 0 or following > 0 or posts > 0:
                            # Extract bio
                            bio_match = re.search(r'"biography":\s*"([^"]*)"', script_content)
                            bio = bio_match.group(1) if bio_match else ''
                            
                            # Extract verification status
                            verified_match = re.search(r'"is_verified":\s*(true|false)', script_content)
                            is_verified = verified_match.group(1) == 'true' if verified_match else False
                            
                            logger.info(f"Extracted from JS: followers={followers}, following={following}, posts={posts}")
                            
                            return {
                                'username': username,
                                'follower_count': followers,
                                'following_count': following,
                                'post_count': posts,
                                'bio_length': len(bio),
                                'has_profile_pic': True,
                                'has_external_url': bool(re.search(r'https?://|www\.', bio)),
                                'avg_likes_per_post': 0,
                                'avg_comments_per_post': 0,
                                'is_private': 'is_private":true' in script_content,
                                'is_verified': is_verified,
                                'biography': bio,
                                'external_url': ''
                            }
                    except:
                        continue
            
            # Strategy 3: Enhanced fallback method
            return self._scrape_fallback_method(soup, username)
            
        except Exception as e:
            logger.error(f"Web direct scraping error for {username}: {str(e)}")
            return None
    
    def _scrape_web_embedded(self, username: str) -> Optional[Dict[str, Any]]:
        """Method 2: Try embedded/oembed endpoints."""
        try:
            # Try Instagram's oembed endpoint
            embed_url = f"https://api.instagram.com/oembed/?url=https://www.instagram.com/{username}/"
            
            response = self.session.get(embed_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'author_name' in data:
                    # This gives limited data, but something is better than nothing
                    return {
                        'username': username,
                        'follower_count': 0,  # Not available in oembed
                        'following_count': 0,  # Not available in oembed
                        'post_count': 0,  # Not available in oembed
                        'bio_length': 0,
                        'has_profile_pic': True,  # Assume true if oembed works
                        'has_external_url': False,
                        'avg_likes_per_post': 0,
                        'avg_comments_per_post': 0,
                        'is_private': False,
                        'is_verified': False,
                        'biography': '',
                        'external_url': ''
                    }
        except:
            pass
        
        return None
    
    def _scrape_instaloader(self, username: str) -> Optional[Dict[str, Any]]:
        """Method 3: Original instaloader method."""
        try:
            profile = self.loader.get_profile(username)
            time.sleep(2)
            
            profile_data = {
                'username': profile.username,
                'follower_count': profile.followers,
                'following_count': profile.followees,
                'post_count': profile.mediacount,
                'bio_length': len(profile.biography) if profile.biography else 0,
                'has_profile_pic': bool(profile.profile_pic_url and not profile.profile_pic_url.endswith('default.jpg')),
                'has_external_url': bool(profile.external_url),
                'is_private': profile.is_private,
                'is_verified': profile.is_verified,
                'biography': profile.biography or '',
                'external_url': profile.external_url or '',
            }
            
            # Try to get engagement data
            avg_likes, avg_comments = self._calculate_engagement(profile)
            profile_data['avg_likes_per_post'] = avg_likes
            profile_data['avg_comments_per_post'] = avg_comments
            
            return profile_data
            
        except instaloader.exceptions.ProfileNotExistsException:
            return None
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            return self._get_limited_private_data(username)
        except Exception as e:
            logger.error(f"Instaloader error: {str(e)}")
            return None
    
    def _scrape_public_api(self, username: str) -> Optional[Dict[str, Any]]:
        """Method 4: Try alternative public APIs or services."""
        try:
            # This is a placeholder for alternative services
            # You could add services like RapidAPI Instagram scrapers here
            # For now, return None to indicate this method is not implemented
            return None
        except:
            return None
    
    def _parse_json_ld_data(self, data: Dict[str, Any], username: str) -> Optional[Dict[str, Any]]:
        """Parse JSON-LD structured data."""
        try:
            return {
                'username': username,
                'follower_count': 0,  # Usually not in JSON-LD
                'following_count': 0,
                'post_count': 0,
                'bio_length': len(data.get('description', '')),
                'has_profile_pic': bool(data.get('image')),
                'has_external_url': bool(data.get('sameAs')),
                'avg_likes_per_post': 0,
                'avg_comments_per_post': 0,
                'is_private': False,
                'is_verified': False,
                'biography': data.get('description', ''),
                'external_url': data.get('sameAs', [''])[0] if data.get('sameAs') else ''
            }
        except:
            return None
    
    def _parse_shared_data(self, data: Dict[str, Any], username: str) -> Optional[Dict[str, Any]]:
        """Parse window._sharedData format."""
        try:
            # Navigate through the nested structure
            entry_data = data.get('entry_data', {})
            profile_page = entry_data.get('ProfilePage', [])
            
            if not profile_page:
                return None
            
            user_data = profile_page[0].get('graphql', {}).get('user', {})
            
            if not user_data:
                return None
            
            return {
                'username': user_data.get('username', username),
                'follower_count': user_data.get('edge_followed_by', {}).get('count', 0),
                'following_count': user_data.get('edge_follow', {}).get('count', 0),
                'post_count': user_data.get('edge_owner_to_timeline_media', {}).get('count', 0),
                'bio_length': len(user_data.get('biography', '')),
                'has_profile_pic': not user_data.get('profile_pic_url', '').endswith('default.jpg'),
                'has_external_url': bool(user_data.get('external_url')),
                'avg_likes_per_post': 0,  # Would need additional API calls
                'avg_comments_per_post': 0,
                'is_private': user_data.get('is_private', False),
                'is_verified': user_data.get('is_verified', False),
                'biography': user_data.get('biography', ''),
                'external_url': user_data.get('external_url', '')
            }
        except Exception as e:
            logger.error(f"Error parsing shared data: {str(e)}")
            return None
    
    def _parse_count_string(self, count_str: str) -> int:
        """Parse count string like '80M', '1,144', '606' to integer."""
        try:
            count_str = count_str.replace(',', '').strip()
            multiplier = 1
            
            if count_str.lower().endswith('k'):
                multiplier = 1000
                count_str = count_str[:-1]
            elif count_str.lower().endswith('m'):
                multiplier = 1000000
                count_str = count_str[:-1]
            elif count_str.lower().endswith('b'):
                multiplier = 1000000000
                count_str = count_str[:-1]
            
            return int(float(count_str) * multiplier)
        except (ValueError, IndexError):
            return 0

    def _extract_count_from_script(self, script_content: str, patterns: list) -> int:
        """Helper method to extract numeric counts from script content using multiple patterns."""
        for pattern in patterns:
            matches = re.findall(pattern, script_content)
            if matches:
                try:
                    return int(matches[0])
                except (ValueError, IndexError):
                    continue
        return 0

    def _parse_api_data(self, data: dict, username: str) -> Optional[Dict[str, Any]]:
        """Parse data from Instagram's mobile API response."""
        try:
            # Navigate through typical API response structure
            user_data = None
            
            # Common paths in Instagram API responses
            possible_paths = [
                ['graphql', 'user'],
                ['data', 'user'],
                ['user'],
                ['items', 0]  # For some API endpoints
            ]
            
            for path in possible_paths:
                current = data
                try:
                    for key in path:
                        if isinstance(key, int):
                            current = current[key]
                        else:
                            current = current.get(key, {})
                    if current and isinstance(current, dict):
                        user_data = current
                        break
                except (KeyError, IndexError, TypeError):
                    continue
            
            if not user_data:
                return None
            
            # Extract data from user object
            return {
                'username': username,
                'follower_count': user_data.get('edge_followed_by', {}).get('count', 
                                                user_data.get('follower_count', 0)),
                'following_count': user_data.get('edge_follow', {}).get('count',
                                                 user_data.get('following_count', 0)),
                'post_count': user_data.get('edge_owner_to_timeline_media', {}).get('count',
                                           user_data.get('media_count', 0)),
                'bio_length': len(user_data.get('biography', '')),
                'has_profile_pic': bool(user_data.get('profile_pic_url')),
                'has_external_url': bool(user_data.get('external_url')),
                'avg_likes_per_post': 0,
                'avg_comments_per_post': 0,
                'is_private': user_data.get('is_private', False),
                'is_verified': user_data.get('is_verified', False),
                'biography': user_data.get('biography', ''),
                'external_url': user_data.get('external_url', '')
            }
            
        except Exception as e:
            logger.error(f"Error parsing API data: {str(e)}")
            return None

    def _scrape_fallback_method(self, soup: BeautifulSoup, username: str) -> Optional[Dict[str, Any]]:
        """Enhanced fallback method using multiple parsing strategies."""
        try:
            logger.info(f"Using fallback method for {username}")
            
            follower_count = 0
            following_count = 0
            post_count = 0
            bio = ''
            has_external_url = False
            is_verified = False
            
            # Strategy 1: Look for meta tags
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                bio = meta_desc.get('content', '')
                logger.info(f"Found bio in meta: {bio[:50]}...")
            
            # Strategy 2: Look for JSON in script tags (alternative patterns)
            for script in soup.find_all('script'):
                if script.string:
                    script_content = script.string
                    
                    # Look for various JSON patterns
                    json_patterns = [
                        r'"edge_followed_by":\s*{"count":\s*(\d+)}',
                        r'"edge_follow":\s*{"count":\s*(\d+)}',
                        r'"edge_owner_to_timeline_media":\s*{"count":\s*(\d+)}',
                        r'followers["\s]*:\s*(\d+)',
                        r'following["\s]*:\s*(\d+)',
                        r'"follower_count":\s*(\d+)',
                        r'"following_count":\s*(\d+)',
                        r'"media_count":\s*(\d+)'
                    ]
                    
                    for i, pattern in enumerate(json_patterns):
                        matches = re.findall(pattern, script_content)
                        if matches:
                            count = int(matches[0])
                            if i < 2:  # followers patterns
                                follower_count = max(follower_count, count)
                            elif i < 4:  # following patterns  
                                following_count = max(following_count, count)
                            elif i >= 4:  # posts patterns
                                post_count = max(post_count, count)
                            
                            logger.info(f"Found count {count} with pattern {i}")
                    
                    # Look for biography in JSON
                    bio_match = re.search(r'"biography":\s*"([^"]*)"', script_content)
                    if bio_match and not bio:
                        bio = bio_match.group(1)
                    
                    # Look for external URL
                    url_match = re.search(r'"external_url":\s*"([^"]*)"', script_content)
                    if url_match:
                        has_external_url = bool(url_match.group(1))
                    
                    # Look for verification
                    verified_match = re.search(r'"is_verified":\s*(true|false)', script_content)
                    if verified_match:
                        is_verified = verified_match.group(1) == 'true'
            
            # Strategy 3: Parse meta description format (Instagram's current format)
            if meta_desc and meta_desc.get('content'):
                meta_content = meta_desc.get('content', '')
                logger.info(f"Parsing meta content: {meta_content}")
                
                # Parse format like "80M Followers, 606 Following, 1,144 Posts"
                meta_patterns = [
                    (r'([\d,]+(?:\.\d+)?[KMBkm]?)\s*Followers', 'followers'),
                    (r'([\d,]+(?:\.\d+)?[KMBkm]?)\s*Following', 'following'),
                    (r'([\d,]+(?:\.\d+)?[KMBkm]?)\s*Posts', 'posts')
                ]
                
                for pattern, type_name in meta_patterns:
                    matches = re.findall(pattern, meta_content, re.IGNORECASE)
                    for match in matches:
                        try:
                            count = self._parse_count_string(match)
                            
                            if type_name == 'followers':
                                follower_count = max(follower_count, count)
                            elif type_name == 'following':
                                following_count = max(following_count, count)
                            elif type_name == 'posts':
                                post_count = max(post_count, count)
                                
                            logger.info(f"Found {type_name}: {count} from meta")
                            
                        except (ValueError, IndexError):
                            continue
            
            # Strategy 4: Parse visible text patterns
            text = soup.get_text()
            
            # Look for number patterns in visible text
            number_patterns = [
                (r'([\d,]+(?:\.\d+)?[KMBkm]?)\s*followers', 'followers'),
                (r'([\d,]+(?:\.\d+)?[KMBkm]?)\s*following', 'following'),
                (r'([\d,]+(?:\.\d+)?[KMBkm]?)\s*posts', 'posts')
            ]
            
            # Only use text patterns if we didn't get data from meta
            if follower_count == 0 and following_count == 0 and post_count == 0:
                for pattern, type_name in number_patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    for match in matches:
                        try:
                            count = self._parse_count_string(match)
                            
                            if type_name == 'followers':
                                follower_count = max(follower_count, count)
                            elif type_name == 'following':
                                following_count = max(following_count, count)
                            elif type_name == 'posts':
                                post_count = max(post_count, count)
                                
                            logger.info(f"Found {type_name}: {count} from text")
                            
                        except (ValueError, IndexError):
                            continue
            
            # If we still don't have bio, try og:description
            if not bio:
                og_desc = soup.find('meta', attrs={'property': 'og:description'})
                if og_desc:
                    bio = og_desc.get('content', '')
            
            # Check for external URL in bio
            if not has_external_url and bio:
                has_external_url = bool(re.search(r'https?://|www\.|\.\w{2,4}/', bio))
            
            logger.info(f"Extracted: followers={follower_count}, following={following_count}, posts={post_count}")
            
            return {
                'username': username,
                'follower_count': follower_count,
                'following_count': following_count,
                'post_count': post_count,
                'bio_length': len(bio),
                'has_profile_pic': True,  # Assume true if we can access the page
                'has_external_url': has_external_url,
                'avg_likes_per_post': 0,  # Can't get this from basic scraping
                'avg_comments_per_post': 0,
                'is_private': 'This account is private' in text,
                'is_verified': is_verified or 'verified' in text.lower(),
                'biography': bio,
                'external_url': ''
            }
            
        except Exception as e:
            logger.error(f"Fallback method error: {str(e)}")
            return None
    
    def _calculate_engagement(self, profile) -> tuple[float, float]:
        """
        Calculate average likes and comments per post.
        
        Args:
            profile: Instaloader Profile object
            
        Returns:
            Tuple of (avg_likes, avg_comments)
        """
        try:
            if profile.is_private:
                # Can't access posts for private profiles
                return 0.0, 0.0
            
            posts = []
            total_likes = 0
            total_comments = 0
            post_count = 0
            
            # Get recent posts (max 12 to avoid rate limiting)
            for post in profile.get_posts():
                if post_count >= 12:
                    break
                
                posts.append(post)
                total_likes += post.likes
                total_comments += post.comments
                post_count += 1
                
                # Add small delay between posts
                time.sleep(0.5)
            
            if post_count > 0:
                avg_likes = total_likes / post_count
                avg_comments = total_comments / post_count
            else:
                avg_likes = 0.0
                avg_comments = 0.0
            
            logger.info(f"Calculated engagement from {post_count} posts: {avg_likes:.1f} likes, {avg_comments:.1f} comments")
            return avg_likes, avg_comments
            
        except Exception as e:
            logger.warning(f"Could not calculate engagement: {str(e)}")
            return 0.0, 0.0
    
    def _get_limited_private_data(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get limited data available for private profiles.
        
        Args:
            username: Instagram username
            
        Returns:
            Dictionary with limited profile data
        """
        try:
            profile = self.loader.get_profile(username)
            
            return {
                'username': profile.username,
                'follower_count': profile.followers if hasattr(profile, 'followers') else 0,
                'following_count': profile.followees if hasattr(profile, 'followees') else 0,
                'post_count': profile.mediacount if hasattr(profile, 'mediacount') else 0,
                'bio_length': len(profile.biography) if profile.biography else 0,
                'has_profile_pic': bool(profile.profile_pic_url and not profile.profile_pic_url.endswith('default.jpg')),
                'has_external_url': bool(profile.external_url),
                'is_private': True,
                'is_verified': profile.is_verified if hasattr(profile, 'is_verified') else False,
                'avg_likes_per_post': 0.0,  # Can't access for private profiles
                'avg_comments_per_post': 0.0,  # Can't access for private profiles
                'biography': profile.biography or '',
                'external_url': profile.external_url or '',
            }
            
        except Exception as e:
            logger.error(f"Could not get limited data for private profile {username}: {str(e)}")
            return None
    
    @staticmethod
    def extract_username_from_url(url: str) -> Optional[str]:
        """
        Extract username from Instagram URL.
        
        Args:
            url: Instagram profile URL
            
        Returns:
            Username string or None if invalid URL
        """
        patterns = [
            r'instagram\.com/([a-zA-Z0-9._]{1,30})/?$',
            r'instagram\.com/([a-zA-Z0-9._]{1,30})/?\?.*$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None


def scrape_instagram_profile(username_or_url: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to scrape Instagram profile.
    
    Args:
        username_or_url: Instagram username or URL
        
    Returns:
        Dictionary with profile data or None if scraping fails
    """
    scraper = InstagramScraper()
    
    # Check if input is URL or username
    if 'instagram.com' in username_or_url:
        username = scraper.extract_username_from_url(username_or_url)
        if not username:
            logger.error(f"Could not extract username from URL: {username_or_url}")
            return None
    else:
        username = username_or_url
    
    return scraper.scrape_profile(username)
