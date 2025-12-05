from pathlib import Path
import os

# === ENVIRONMENT VARIABLES ===
GOOGLE_OAUTH2_CLIENT_ID = os.getenv('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET')
DB_HOST = os.getenv('HOST1')
DB_PASSWORD = os.getenv('PASSWORD1')
SECRET_KEY = os.getenv('SECRET')

# === BASE PROJECT PATH ===
BASE_DIR = Path(__file__).resolve().parent.parent

# === DEBUG / DEPLOYMENT ===
DEBUG = False
ALLOWED_HOSTS = ['proprelims.fly.dev', 'proprelims.com', 'www.proprelims.com']

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = ['https://proprelims.fly.dev']

# === APPLICATIONS ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Local app
    'quiz',
    # 3rd Party
    'django_htmx',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'django.contrib.sitemaps'
]

# === MIDDLEWARE ===
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
]

# Security for production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# === URLS / WSGI ===
ROOT_URLCONF = 'proprelims.urls'
WSGI_APPLICATION = 'proprelims.wsgi.application'

# === TEMPLATES ===
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# === DATABASE ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': '',
        'USER': '',
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': '5432',
        'OPTIONS': {'sslmode': 'require'},
        'CONN_MAX_AGE': 600,  # Added for connection pooling
    }
}

# === PASSWORD VALIDATION ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === LANGUAGE / TIMEZONE ===
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# === STATIC FILES ===
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# === PRIMARY KEY FIELD TYPE ===
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# === SITE CONFIGURATION ===
SITE_ID = 1

# === AUTH BACKENDS ===
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# === DJANGO-ALLAUTH CONFIGURATION ===
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = 'username'
ACCOUNT_USER_MODEL_EMAIL_FIELD = 'email'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5
ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# === CUSTOM SIGNUP FORM (with terms checkbox) ===
ACCOUNT_FORMS = {
    'signup': 'quiz.forms.CustomSignupForm',
}

# === SOCIALACCOUNT SETTINGS ===
SOCIALACCOUNT_ADAPTER = 'quiz.adapters.CustomSocialAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = False
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_LOGIN_ON_GET = True

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
        'OAUTH_PKCE_ENABLED': True,
    }
}

# For production:
# ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Pro Prelims]'
SITE_ID = 1

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''  
DEFAULT_FROM_EMAIL = ''

RATELIMIT_VIEW = 'quiz.views.rate_limit_exceeded'
