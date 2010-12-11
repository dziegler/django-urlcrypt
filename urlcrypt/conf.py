import os

from django.conf import settings

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = getattr(settings, 'SECRET_KEY', 'sekrit')
RUNNING_TESTS = getattr(settings, 'RUNNING_TESTS', False)

if RUNNING_TESTS:
    URLCRYPT_PRIVATE_KEY_PATH = os.path.join(SCRIPT_DIR, "test", "test_private_key")
    if not os.path.exists(URLCRYPT_PRIVATE_KEY_PATH):
        URLCRYPT_PRIVATE_KEY_PATH = None
else:
    URLCRYPT_PRIVATE_KEY_PATH = getattr(settings, 'URLCRYPT_PRIVATE_KEY_PATH', None)


URLCRYPT_USE_RSA_ENCRYPTION = URLCRYPT_PRIVATE_KEY_PATH is not None
URLCRYPT_LOGIN_URL = getattr(settings, 'URLCRYPT_LOGIN_URL', settings.LOGIN_URL)
URLCRYPT_RATE_LIMIT = getattr(settings, 'URLCRYPT_RATE_LIMIT', 60)