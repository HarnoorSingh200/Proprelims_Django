from allauth.account.forms import SignupForm
from django import forms

class CustomSignupForm(SignupForm):
    accept_terms = forms.BooleanField(
        label="I agree to the Terms of Service and Privacy Policy",
        error_messages={'required': 'You must accept the terms to register.'}
    )

    def save(self, request):
        # Save the user first
        user = super().save(request)
        # Optionally log this acceptance or send an email
        return user
