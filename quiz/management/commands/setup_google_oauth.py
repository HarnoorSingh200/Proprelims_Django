from django.core.management.base import BaseCommand
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Setup Google OAuth application'

    def handle(self, *args, **options):
        if not settings.GOOGLE_OAUTH2_CLIENT_ID or not settings.GOOGLE_OAUTH2_CLIENT_SECRET:
            self.stdout.write(
                self.style.ERROR('Google OAuth credentials not found in environment variables')
            )
            self.stdout.write('Make sure you have set:')
            self.stdout.write('1080241553365-rp57l5hk3srpafedog6nodlm1i5gu2u6.apps.googleusercontent.com')
            self.stdout.write('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')
            return

        try:
            site = Site.objects.get(pk=settings.SITE_ID)
        except Site.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Site with ID {settings.SITE_ID} does not exist')
            )
            return

        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
                'secret': settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            }
        )

        if not created:
            # Update existing app with new credentials
            google_app.client_id = settings.GOOGLE_OAUTH2_CLIENT_ID
            google_app.secret = settings.GOOGLE_OAUTH2_CLIENT_SECRET
            google_app.save()

        # Add site to the app
        google_app.sites.add(site)

        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(f'{action} Google OAuth application successfully')
        )

        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Make sure your Google Cloud Console OAuth app has these redirect URIs:')
        self.stdout.write('   - http://localhost:8000/accounts/google/login/callback/')
        self.stdout.write('   - http://127.0.0.1:8000/accounts/google/login/callback/')
        self.stdout.write('2. Test the Google login at: http://localhost:8000/accounts/login/')