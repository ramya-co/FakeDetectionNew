#!/usr/bin/env python
import os
import sys
import django

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fake_account_detection.settings')
django.setup()

from detector.scraper import InstagramScraper

def test_scraper():
    print("Testing enhanced Instagram scraper...")
    scraper = InstagramScraper()
    
    # Test with a popular account
    username = 'katrinakaif'
    print(f"\nTesting with username: {username}")
    
    result = scraper.scrape_profile(username)
    
    if result:
        print("\n✅ Scraping successful!")
        print("=" * 50)
        for key, value in result.items():
            print(f"{key:20}: {value}")
        print("=" * 50)
        
        # Check if we got meaningful data
        if result.get('follower_count', 0) > 0:
            print("🎉 Successfully extracted follower count!")
        else:
            print("⚠️  Follower count is 0, fallback method used")
            
    else:
        print("❌ Scraping failed")

if __name__ == "__main__":
    test_scraper()
