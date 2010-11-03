import os

from urlcrypt.conf import URLCRYPT_PRIVATE_KEY_PATH
from urlcrypt.oaep import OAEP

# load the private key from the specified file
from Crypto.PublicKey import RSA 
 
with open(URLCRYPT_PRIVATE_KEY_PATH) as f: 
    pem_private_key = f.read() 

PRIVATE_KEY = RSA.importKey(pem_private_key)
KEY_LENGTH_BYTES = int((PRIVATE_KEY.size() + 1) / 8)
PADDER = OAEP(os.urandom)
BLOCK_BYTES = KEY_LENGTH_BYTES - 2 * 20 - 2 # from oaep.py

def split_string(s, block_size):
    blocks = []
    start = 0
    while start < len(s):
        block = s[start:start+block_size]
        blocks.append(block)
        start += block_size
    return blocks

def encrypt(s):
    encrypted_blocks = []
    for block in split_string(s, BLOCK_BYTES):
        padded_block = PADDER.encode(KEY_LENGTH_BYTES, block) # will raise ValueError if token is too long
        encrypted_block = PRIVATE_KEY.encrypt(padded_block, None)[0]
        encrypted_blocks.append(encrypted_block)
    return ''.join(encrypted_blocks)
    
def decrypt(s):
    decrypted_blocks = []
    for block in split_string(s, KEY_LENGTH_BYTES):
        padded_block = '\x00' + PRIVATE_KEY.decrypt(block) # NUL byte is apparently dropped by decryption
        decrypted_block = PADDER.decode(KEY_LENGTH_BYTES, padded_block) # will raise ValueError on corrupt token
        decrypted_blocks.append(decrypted_block)
    return ''.join(decrypted_blocks)