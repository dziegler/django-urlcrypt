import base64
import hashlib
import hmac
import time

try:
    from hashlib import sha1 as sha_hmac
except ImportError:
    import sha as sha_hmac

from django.contrib.auth.models import User

from urlcrypt.conf import SECRET_KEY, URLCRYPT_USE_RSA_ENCRYPTION

if URLCRYPT_USE_RSA_ENCRYPTION:
    import urlcrypt.rsa

# generate a key for obfuscation
# kind of ghetto, is there a better way to do this other than os.urandom?
OBFUSCATE_KEY = hashlib.sha512(SECRET_KEY).digest() + hashlib.sha512(SECRET_KEY[::-1]).digest()

def base64url_encode(text):
    padded_b64 = base64.urlsafe_b64encode(text)
    return padded_b64.replace('=', '') # = is a reserved char
    
def base64url_decode(raw_b64):
    # calculate padding characters
    if len(raw_b64) % 4 == 0:
        padding = ''
    else:
        padding = (4 - (len(raw_b64) % 4)) * '='
    padded_b64 = raw_b64 + padding
    return base64.urlsafe_b64decode(padded_b64)
    
def pack(*strings):
    assert '|' not in ''.join(strings)
    return '|'.join(strings)
    
def unpack(packed_string):
    return packed_string.split('|')

def obfuscate(text):
    # copy out our OBFUSCATE_KEY to the length of the text
    key = OBFUSCATE_KEY * (len(text)//len(OBFUSCATE_KEY) + 1)

    # XOR each character from our input with the corresponding character
    # from the key
    xor_gen = (chr(ord(t) ^ ord(k)) for t, k in zip(text, key))
    return ''.join(xor_gen)

deobfuscate = obfuscate

def encode_token(strings):
    secret_key = secret_key_f(*strings)
    signature = hmac.new(str(secret_key), pack(*strings), sha_hmac).hexdigest()
    packed_string = pack(signature, *strings)
    return obfuscate(packed_string)

def decode_token(token, keys):
    packed_string = deobfuscate(token)
    strings = unpack(packed_string)[1:]
    assert token == encode_token(strings)
    return dict(zip(keys, strings))

def secret_key_f(user_id, *args):
    # generate a secret key given the user id
    user = User.objects.get(id=int(user_id))
    return user.password + SECRET_KEY

def generate_login_token(user, url):
    strings = [str(user.id), url.strip(), str(int(time.time()))]
    token_byte_string = encode_token(strings)
    
    if URLCRYPT_USE_RSA_ENCRYPTION:
        token_byte_string = urlcrypt.rsa.encrypt(token_byte_string)
    
    return base64url_encode(token_byte_string)

def decode_login_token(token):
    token_byte_string = base64url_decode(str(token))
    
    if URLCRYPT_USE_RSA_ENCRYPTION:
        token_byte_string = urlcrypt.rsa.decrypt(token_byte_string)
        
    keys = ('user_id', 'url', 'timestamp')
    data = decode_token(token_byte_string, keys)
    data['user_id'] = int(data['user_id'])
    data['timestamp'] = int(data['timestamp'])
    return data
