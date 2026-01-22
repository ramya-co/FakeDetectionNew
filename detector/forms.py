"""
Django forms for Instagram account analysis.
"""
from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import re


class ManualInputForm(forms.Form):
    """Form for manual input of Instagram account features."""
    
    username = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Instagram username',
            'class': 'form-control'
        }),
        help_text="Instagram username (without @)"
    )
    
    follower_count = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Number of followers"
    )
    
    following_count = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Number of accounts following"
    )
    
    post_count = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Total number of posts"
    )
    
    bio_length = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Length of bio text (character count)"
    )
    
    has_profile_pic = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Check if account has a profile picture"
    )
    
    has_external_url = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Check if account has external URL in bio"
    )
    
    avg_likes_per_post = forms.FloatField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0.0',
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text="Average number of likes per post"
    )
    
    avg_comments_per_post = forms.FloatField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0.0',
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text="Average number of comments per post"
    )
    
    def clean_username(self):
        """Validate username format."""
        username = self.cleaned_data['username'].strip()
        
        # Remove @ if present
        if username.startswith('@'):
            username = username[1:]
        
        # Validate Instagram username format
        if not re.match(r'^[a-zA-Z0-9._]{1,30}$', username):
            raise ValidationError(
                "Invalid username format. Instagram usernames can only contain "
                "letters, numbers, periods, and underscores, and be up to 30 characters long."
            )
        
        return username


class URLInputForm(forms.Form):
    """Form for Instagram URL input."""
    
    instagram_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'placeholder': 'https://www.instagram.com/username/',
            'class': 'form-control'
        }),
        help_text="Full Instagram profile URL"
    )
    
    def clean_instagram_url(self):
        """Validate that the URL is a valid Instagram profile URL."""
        url = self.cleaned_data['instagram_url'].strip()
        
        # Check if it's a valid Instagram URL
        instagram_patterns = [
            r'^https?://(?:www\.)?instagram\.com/([a-zA-Z0-9._]{1,30})/?$',
            r'^https?://(?:www\.)?instagram\.com/([a-zA-Z0-9._]{1,30})/?\?.*$',
        ]
        
        is_valid = False
        for pattern in instagram_patterns:
            if re.match(pattern, url):
                is_valid = True
                break
        
        if not is_valid:
            raise ValidationError(
                "Please enter a valid Instagram profile URL. "
                "Example: https://www.instagram.com/username/"
            )
        
        return url
    
    def get_username_from_url(self):
        """Extract username from validated Instagram URL."""
        if hasattr(self, 'cleaned_data') and 'instagram_url' in self.cleaned_data:
            url = self.cleaned_data['instagram_url']
            match = re.search(r'instagram\.com/([a-zA-Z0-9._]{1,30})', url)
            if match:
                return match.group(1)
        return None


# ============= TWITTER/X FORMS =============

class TwitterManualForm(forms.Form):
    """Form for manual input of Twitter account features."""
    
    username = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Twitter/X username',
            'class': 'form-control'
        }),
        help_text="Twitter username (without @)"
    )
    
    follower_count = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Number of followers"
    )
    
    following_count = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Number of accounts following"
    )
    
    post_count = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Total number of tweets"
    )
    
    bio_length = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Length of bio text (character count)"
    )
    
    has_profile_pic = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Check if account has a profile picture"
    )
    
    has_external_url = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Check if account has external URL in bio"
    )
    
    avg_likes_per_post = forms.FloatField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0.0',
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text="Average number of likes per tweet"
    )
    
    avg_comments_per_post = forms.FloatField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0.0',
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text="Average number of replies/retweets per tweet"
    )
    
    def clean_username(self):
        """Validate username format."""
        username = self.cleaned_data['username'].strip()
        
        # Remove @ if present
        if username.startswith('@'):
            username = username[1:]
        
        # Validate Twitter username format (alphanumeric and underscore, 1-15 chars)
        if not re.match(r'^[a-zA-Z0-9_]{1,15}$', username):
            raise ValidationError(
                "Invalid username format. Twitter usernames can only contain "
                "letters, numbers, and underscores, and be up to 15 characters long."
            )
        
        return username


class TwitterURLForm(forms.Form):
    """Form for Twitter URL input."""
    
    twitter_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'placeholder': 'https://twitter.com/username or https://x.com/username',
            'class': 'form-control'
        }),
        help_text="Full Twitter/X profile URL"
    )
    
    def clean_twitter_url(self):
        """Validate that the URL is a valid Twitter profile URL."""
        url = self.cleaned_data['twitter_url'].strip()
        
        # Check if it's a valid Twitter/X URL
        twitter_patterns = [
            r'^https?://(?:www\.)?(twitter\.com|x\.com)/([a-zA-Z0-9_]{1,15})/?$',
            r'^https?://(?:www\.)?(twitter\.com|x\.com)/([a-zA-Z0-9_]{1,15})/?\?.*$',
        ]
        
        is_valid = False
        for pattern in twitter_patterns:
            if re.match(pattern, url):
                is_valid = True
                break
        
        if not is_valid:
            raise ValidationError(
                "Please enter a valid Twitter/X profile URL. "
                "Example: https://twitter.com/username or https://x.com/username"
            )
        
        return url
    
    def get_username_from_url(self):
        """Extract username from validated Twitter URL."""
        if hasattr(self, 'cleaned_data') and 'twitter_url' in self.cleaned_data:
            url = self.cleaned_data['twitter_url']
            match = re.search(r'(?:twitter\.com|x\.com)/([a-zA-Z0-9_]{1,15})', url)
            if match:
                return match.group(1)
        return None


# ============= FACEBOOK FORMS =============

class FacebookManualForm(forms.Form):
    """Form for manual input of Facebook account features."""
    
    username = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter Facebook username or name',
            'class': 'form-control'
        }),
        help_text="Facebook username or display name"
    )
    
    follower_count = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Number of friends or followers"
    )
    
    following_count = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Number of pages/people following (if available)"
    )
    
    post_count = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Total number of posts"
    )
    
    bio_length = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0',
            'class': 'form-control'
        }),
        help_text="Length of bio/about section (character count)"
    )
    
    has_profile_pic = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Check if account has a profile picture"
    )
    
    has_external_url = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text="Check if account has external URL/website"
    )
    
    avg_likes_per_post = forms.FloatField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0.0',
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text="Average number of likes per post"
    )
    
    avg_comments_per_post = forms.FloatField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'placeholder': '0.0',
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text="Average number of comments per post"
    )
    
    def clean_username(self):
        """Validate username format."""
        username = self.cleaned_data['username'].strip()
        
        # Facebook usernames are more flexible, just ensure it's not empty
        if len(username) < 1:
            raise ValidationError("Username cannot be empty.")
        
        return username


class FacebookURLForm(forms.Form):
    """Form for Facebook URL input."""
    
    facebook_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'placeholder': 'https://www.facebook.com/username',
            'class': 'form-control'
        }),
        help_text="Full Facebook profile URL"
    )
    
    def clean_facebook_url(self):
        """Validate that the URL is a valid Facebook profile URL."""
        url = self.cleaned_data['facebook_url'].strip()
        
        # Check if it's a valid Facebook URL
        facebook_patterns = [
            r'^https?://(?:www\.)?(facebook\.com|fb\.com)/[^/?]+/?.*$',
            r'^https?://(?:www\.)?facebook\.com/profile\.php\?id=\d+',
            r'^https?://(?:www\.)?facebook\.com/people/[^/]+/\d+',
        ]
        
        is_valid = False
        for pattern in facebook_patterns:
            if re.match(pattern, url):
                is_valid = True
                break
        
        if not is_valid:
            raise ValidationError(
                "Please enter a valid Facebook profile URL. "
                "Example: https://www.facebook.com/username"
            )
        
        return url
    
    def get_username_from_url(self):
        """Extract username from validated Facebook URL."""
        if hasattr(self, 'cleaned_data') and 'facebook_url' in self.cleaned_data:
            url = self.cleaned_data['facebook_url']
            
            # Try different patterns
            patterns = [
                r'facebook\.com/(?:profile\.php\?id=)?([^/?]+)',
                r'fb\.com/([^/?]+)',
                r'facebook\.com/people/[^/]+/(\d+)',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
        return None
