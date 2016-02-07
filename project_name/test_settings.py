import os

from settings import *

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

DEBUG = True

COMPRESS_ENABLED = False
MEDIA_ROOT = os.path.join(BASE_DIR, 'media-test/')

# Re assigning because debug_toolbar should not be included while testing
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
