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

########## EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_PORT = 587
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'django.inventory@gmail.com'
EMAIL_HOST_PASSWORD = 'inventoryjtg'
DEFAULT_FROM_EMAIL = 'Django Inventory App <django.inventory@gmail.com>'
EMAIL_USE_TLS = True
########## END EMAIL CONFIGURATION