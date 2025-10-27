# users/adapters.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import reverse

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Overrides the default redirect behavior after a social connect.
        """
        # A 'socialconnect' is when a social account is linked to an existing user.
        # We can just redirect them to their dashboard.
        return reverse('dashboard')

    def get_signup_redirect_url(self, request, sociallogin):
        """
        Overrides the default redirect behavior after a new social signup.
        """
        # After a new user signs up via Google, they have no user_type.
        # We redirect them to our 'choose_user_role' page to select one.
        return reverse('choose_user_role')