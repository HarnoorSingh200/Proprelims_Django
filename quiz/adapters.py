# Create this file: quiz/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
import re


from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from .models import UserProfile  # Ensure this is imported

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login. Generates a unique username
        and redirects to terms acceptance if not already accepted.
        """
        user = super().save_user(request, sociallogin, form)

        # Username generation logic (unchanged)
        if not user.username or user.username == user.email:
            email = user.email
            if email:
                base_username = email.split('@')[0]
                base_username = re.sub(r'[^\w]', '_', base_username)
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1
                user.username = username
                user.save()

        # Check if the user has accepted terms
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if not profile.terms_accepted_at:
            request.session['pending_social_user_id'] = user.id
            raise ImmediateHttpResponse(redirect('accept_terms'))

        return user

    def pre_social_login(self, request, sociallogin):
        """Automatically link social account to existing user with same email"""
        if sociallogin.is_existing:
            return  # already logged in

        email_address = sociallogin.account.extra_data.get('email')
        if not email_address:
            return

        try:
            user = User.objects.get(email=email_address)
        except User.DoesNotExist:
            return

        # Link this social login to the existing user
        sociallogin.connect(request, user)

    def populate_user(self, request, sociallogin, data):
        """
        Populates user information from social provider info.
        """
        user = super().populate_user(request, sociallogin, data)

        # Get additional info from Google
        if sociallogin.account.provider == 'google':
            extra_data = sociallogin.account.extra_data

            # If we have a name from Google, we could use it for username
            if not user.username and 'name' in extra_data:
                name = extra_data['name']
                # Create username from name
                base_username = re.sub(r'[^\w\s]', '', name.lower()).replace(' ', '_')

                # Ensure username is unique
                username = base_username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1

                user.username = username

        return user