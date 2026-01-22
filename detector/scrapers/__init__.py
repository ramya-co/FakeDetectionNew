"""
Scrapers package for multi-platform social media account data extraction.
"""
from .instagram_scraper import scrape_instagram_profile
from .twitter_scraper import scrape_twitter_profile
from .facebook_scraper import scrape_facebook_profile

__all__ = [
    'scrape_instagram_profile',
    'scrape_twitter_profile',
    'scrape_facebook_profile',
]
