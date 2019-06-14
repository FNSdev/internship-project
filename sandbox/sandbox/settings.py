from sandbox.base_settings import *


# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = False

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '0.0.0.0',
]

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Github integration

GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')

# Celery

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_BEAT_SCHEDULE = {
    'test-task': {
        'task': 'core.tasks.test',
        'schedule': 5,
    }
}
