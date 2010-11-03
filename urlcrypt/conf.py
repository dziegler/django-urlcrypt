import os

from django.conf import settings

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

SECRET_KEY = getattr(settings, 'SECRET_KEY', 'sekrit')
RUNNING_TESTS = getattr(settings, 'RUNNING_TESTS', False)
RUNNING_TESTS = True

# Changing this setting, or SECRET_KEY, invalidates existing tokens, the pycrypto library is required if enabled
URLCRYPT_USE_RSA_ENCRYPTION = getattr(settings, 'URLCRYPT_USE_RSA_ENCRYPTION', False)
# if URLCRYPT_USE_RSA_ENCRYPTION is True, the path to an RSA private key file must be set here

if RUNNING_TESTS:
    URLCRYPT_PRIVATE_KEY_PATH = os.path.join(SCRIPT_DIR, "test", "test_private_key")
else:
    URLCRYPT_PRIVATE_KEY_PATH = getattr(settings, 'URLCRYPT_PRIVATE_KEY_PATH', None)

if URLCRYPT_USE_RSA_ENCRYPTION and URLCRYPT_PRIVATE_KEY_PATH is None:
    raise Exception("When using URLCRYPT_USE_RSA_ENCRYPTION you must set URLCRYPT_PRIVATE_KEY_PATH to the path of your private key")

URLCRYPT_LOGIN_URL = getattr(settings, 'URLCRYPT_LOGIN_URL', settings.LOGIN_URL)
URLCRYPT_RATE_LIMIT = getattr(settings, 'URLCRYPT_RATE_LIMIT', 60)