from django.core.management.base import BaseCommand
from detector.scraper import InstagramScraper

class Command(BaseCommand):
    help = 'Test Instagram scraper functionality'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Instagram username to test')

    def handle(self, *args, **options):
        username = options['username']
        
        self.stdout.write(f"Testing enhanced Instagram scraper with: {username}")
        
        scraper = InstagramScraper()
        result = scraper.scrape_profile(username)
        
        if result:
            self.stdout.write(self.style.SUCCESS("✅ Scraping successful!"))
            self.stdout.write("=" * 60)
            
            for key, value in result.items():
                self.stdout.write(f"{key:20}: {value}")
            
            self.stdout.write("=" * 60)
            
            # Check if we got meaningful data
            if result.get('follower_count', 0) > 0:
                self.stdout.write(self.style.SUCCESS("🎉 Successfully extracted follower count!"))
            else:
                self.stdout.write(self.style.WARNING("⚠️  Follower count is 0, fallback method used"))
                
        else:
            self.stdout.write(self.style.ERROR("❌ Scraping failed"))
