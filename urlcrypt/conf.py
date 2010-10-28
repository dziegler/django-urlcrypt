import hashlib

from django.conf import settings

SECRET_KEY = settings.SECRET_KEY
# kind of ghetto, is there a better way to do this other than os.urandom?
OBFUSCATE_KEY = hashlib.sha512(SECRET_KEY).digest() + hashlib.sha512(SECRET_KEY[::-1]).digest()

URLCRYPT_LOGIN_URL = getattr(settings, 'URLCRYPT_LOGIN_URL', settings.LOGIN_URL)
RUNNING_TESTS = getattr(settings, 'RUNNING_TESTS', False)
