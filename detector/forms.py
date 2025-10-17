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
