# A library for safely encoding and obfuscating data in urls

import base64
import hmac
import itertools
import time

try:
    from hashlib import sha1 as sha_hmac
except ImportError:
    import sha as sha_hmac

try:
    from urlcrypt.conf import OBFUSCATE_KEY, SECRET_KEY
except ImportError:
    SECRET_KEY = 'sekrit'
    OBFUSCATE_KEY = 'supersekrit'

def obfuscate(text):
    # copy out our OBFUSCATE_KEY to the length of the text
    key = OBFUSCATE_KEY * (len(text)//len(OBFUSCATE_KEY) + 1)
    
    # XOR each character from our input with the corresponding character
    # from the key
    xor_gen = (chr(ord(t) ^ ord(k)) for t, k in zip(text, key))
    return ''.join(xor_gen)

deobfuscate = obfuscate

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

def generate_login_token(user, url):
    return encode_token(*map(str, (user.id, user.password, url.strip(), int(time.time()))))

def decode_login_token(token):
    data = decode_token(str(token), ('user_id', 'password', 'url', 'timestamp'))
    data['user_id'] = int(data['user_id'])
    return data

def encode_token(*strings):
    token = ''.join(itertools.chain(strings, (SECRET_KEY,)))
    token_hash = hmac.new(SECRET_KEY, token, sha_hmac).hexdigest()
    packed_string = pack(token_hash, *strings)
    obfuscated_string = obfuscate(packed_string)
    return base64url_encode(obfuscated_string)
    
def decode_token(token, keys):
    # if you add more fields, you need to use .get() so that old tokens
    # don't cause a KeyError
    obfuscated_string = base64url_decode(token)
    packed_string = deobfuscate(obfuscated_string)
    strings = unpack(packed_string)[1:]
    assert token == encode_token(*strings)
    return dict(zip(keys, strings))

if __name__ == '__main__':
    message = {
        'url': u'/users/following', 
        'user_id': '12345'
    }
    
    token = encode_token(message['user_id'], message['url'])
    decoded_message = decode_token(token,('user_id', 'url', 'timestamp'))
    print 'token: {0}'.format(token)
    print 'token length: {0}'.format(len(token))
    print 'decoded: {0}'.format(decoded_message)
    for key, val in message.iteritems():
        assert val == decoded_message[key]
