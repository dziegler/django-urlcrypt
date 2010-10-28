import hashlib

from django.conf import settings

SECRET_KEY = settings.SECRET_KEY

# let's make this really long
OBFUSCATE_KEY = hashlib.sha512(SECRET_KEY[:10]).digest() + hashlib.sha512(SECRET_KEY[10:]).digest() 

URLCRYPT_LOGIN_URL = getattr(settings, 'URLCRYPT_LOGIN_URL', settings.LOGIN_URL)
RUNNING_TESTS = getattr(settings, 'RUNNING_TESTS', False)
